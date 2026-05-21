import json
import time

import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO

CONFIDENCE_THRESHOLD = 0.5
LATENCY_THRESHOLD_MS = 200
RESULTS_FILE = '/app/perception_results.json'
SCENE_CAPTURE_FILE = '/app/scene_capture.jpg'


class PerceptionNode(Node):

    def __init__(self):
        super().__init__('perception_node')
        self.bridge = CvBridge()
        self.model = YOLO('yolov8n.pt')
        self.get_logger().info('YOLOv8n model loaded')

        self.frames_processed = 0
        self.frames_with_detections = 0
        self.all_detections = []
        self.latencies = []
        self.latest_frame = None

        self.create_subscription(Image, '/uav/camera', self.camera_callback, 10)
        self.get_logger().info('Subscribed to /uav/camera')

    def camera_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().warn(f'Frame decode error: {e}')
            return

        self.latest_frame = frame
        self.frames_processed += 1

        t0 = time.time()
        results = self.model(frame, verbose=False)
        latency_ms = (time.time() - t0) * 1000
        self.latencies.append(latency_ms)

        detections = [
            {
                'class': self.model.names[int(box.cls[0])],
                'confidence': round(float(box.conf[0]), 3),
            }
            for result in results
            for box in result.boxes
            if float(box.conf[0]) >= CONFIDENCE_THRESHOLD
        ]

        if detections:
            self.frames_with_detections += 1
            self.all_detections.extend(detections)

        self.get_logger().info(
            f'Frame {self.frames_processed}: {len(detections)} detections '
            f'| latency {latency_ms:.0f}ms'
        )

        # Write results after every frame so the file survives a SIGTERM kill
        self.save_results()

    def save_results(self):
        if self.latest_frame is not None:
            cv2.imwrite(SCENE_CAPTURE_FILE, self.latest_frame)
            self.get_logger().info(f'Scene capture saved → {SCENE_CAPTURE_FILE}')

        avg_latency = (
            round(sum(self.latencies) / len(self.latencies), 1)
            if self.latencies else 0.0
        )
        detected_classes = sorted(set(d['class'] for d in self.all_detections))
        max_confidence = max(
            (d['confidence'] for d in self.all_detections), default=0.0
        )

        passed = (
            self.frames_processed > 0
            and avg_latency < LATENCY_THRESHOLD_MS
        )

        output = {
            'test_passed': passed,
            'model': 'yolov8n',
            'frames_processed': self.frames_processed,
            'frames_with_detections': self.frames_with_detections,
            'detection_rate': round(
                self.frames_with_detections / self.frames_processed, 3
            ) if self.frames_processed > 0 else 0.0,
            'avg_latency_ms': avg_latency,
            'max_confidence': round(max_confidence, 3),
            'detected_classes': detected_classes,
            'thresholds': {
                'min_confidence': CONFIDENCE_THRESHOLD,
                'max_latency_ms': LATENCY_THRESHOLD_MS,
            },
        }

        with open(RESULTS_FILE, 'w') as f:
            json.dump(output, f, indent=2)

        self.get_logger().info(
            f'Results saved → {RESULTS_FILE} | '
            f'frames: {self.frames_processed} | '
            f'with detections: {self.frames_with_detections} | '
            f'avg latency: {avg_latency}ms'
        )


def main(args=None):
    rclpy.init(args=args)
    node = PerceptionNode()
    try:
        rclpy.spin(node)
    except Exception:
        pass
    finally:
        node.save_results()
        node.destroy_node()
        rclpy.shutdown()
