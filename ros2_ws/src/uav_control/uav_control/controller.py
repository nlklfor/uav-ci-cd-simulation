import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class UAVController(Node):

    def __init__(self):
        super().__init__('uav_controller')

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        self.timer = self.create_timer(1.0, self.send_command)

    def send_command(self):
        msg = Twist()

        msg.linear.x = 1.0
        msg.linear.z = 0.5

        self.publisher.publish(msg)

        self.get_logger().info('Sending velocity command')


def main(args=None):
    rclpy.init(args=args)
    node = UAVController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()