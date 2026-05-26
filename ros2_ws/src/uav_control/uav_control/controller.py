import math
import json
import os
import random

import cv2
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

# Seeded randomness: same seed → identical run, different seed → different conditions
SEED = int(os.environ.get('RANDOM_SEED', 42))
_rng = random.Random(SEED)

TARGET = (50.0, 30.0, 0.0)
TOLERANCE = 0.5
TIMEOUT = 20.0
METRICS_FILE = '/app/metrics.json'

# Seed controls max speed — simulates varying wind / motor conditions
MAX_SPEED = round(0.7 + _rng.random() * 0.6, 3)  # range: 0.7–1.3 m/s


class UAVController(Node):

    def __init__(self):
        super().__init__('uav_controller')

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(Odometry, '/model/uav/odometry', self.odom_callback, 10)

        self.position = None
        self.mission_done = False
        self.start_time = self.get_clock().now()
        self.bridge = CvBridge()
        self.latest_frame = None

        self.create_subscription(Image, '/uav/camera', self.camera_callback, 10)
        self.create_timer(0.1, self.fly_to_target)

    def camera_callback(self, msg):
        try:
            self.latest_frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().warn(f'Camera decode error: {e}')

    def odom_callback(self, msg):
        pos = msg.pose.pose.position
        self.position = (pos.x, pos.y, pos.z)

    def fly_to_target(self):
        if self.mission_done:
            return

        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9

        if elapsed > TIMEOUT and self.position is None:
            self.get_logger().error('TIMEOUT — no odometry received, simulation likely failed')
            self.mission_done = True
            metrics = {
                'mission_success': False,
                'seed': SEED,
                'max_speed_ms': MAX_SPEED,
                'target': {'x': TARGET[0], 'y': TARGET[1], 'z': TARGET[2]},
                'final_position': {'x': 0.0, 'y': 0.0, 'z': 0.0},
                'deviation_from_target_m': -1.0,
                'flight_time_s': round(elapsed, 2),
            }
            with open(METRICS_FILE, 'w') as f:
                json.dump(metrics, f, indent=2)
            rclpy.shutdown()
            return

        if self.position is None:
            return

        cx, cy, cz = self.position
        tx, ty, tz = TARGET

        ex, ey, ez = tx - cx, ty - cy, tz - cz
        distance = math.sqrt(ex**2 + ey**2 + ez**2)

        if distance < TOLERANCE:
            self.get_logger().info(f'TARGET REACHED — distance: {distance:.2f}m')
            self.finish(success=True, distance=distance)
            return

        if elapsed > TIMEOUT:
            self.get_logger().info(f'TIMEOUT — final distance to target: {distance:.2f}m')
            self.finish(success=False, distance=distance)
            return

        k = 0.5
        msg = Twist()
        msg.linear.x = max(-MAX_SPEED, min(MAX_SPEED, k * ex))
        msg.linear.y = max(-MAX_SPEED, min(MAX_SPEED, k * ey))
        msg.linear.z = max(-MAX_SPEED, min(MAX_SPEED, k * ez))
        self.publisher.publish(msg)

        self.get_logger().info(
            f'pos: ({cx:.1f}, {cy:.1f}, {cz:.1f}) | distance to B: {distance:.2f}m | t: {elapsed:.1f}s'
        )

    def finish(self, success, distance):
        self.mission_done = True
        cx, cy, cz = self.position
        metrics = {
            'mission_success': success,
            'seed': SEED,
            'max_speed_ms': MAX_SPEED,
            'target': {'x': TARGET[0], 'y': TARGET[1], 'z': TARGET[2]},
            'final_position': {'x': round(cx, 2), 'y': round(cy, 2), 'z': round(cz, 2)},
            'deviation_from_target_m': round(distance, 3),
            'flight_time_s': round((self.get_clock().now() - self.start_time).nanoseconds / 1e9, 2),
        }
        with open(METRICS_FILE, 'w') as f:
            json.dump(metrics, f, indent=2)
        self.get_logger().info(f'Metrics saved → {METRICS_FILE}')

        if self.latest_frame is not None:
            cv2.imwrite('/app/scene_capture.jpg', self.latest_frame)
            self.get_logger().info('Scene capture saved → /app/scene_capture.jpg')

        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = UAVController()
    rclpy.spin(node)
    node.destroy_node()
