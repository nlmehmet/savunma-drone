"""Publishes a still image on /camera/image_raw to test nodes without Gazebo."""
import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from ultralytics.utils import ASSETS

from savunma_drone.image_utils import bgr_to_msg


class TestImagePublisher(Node):

    def __init__(self):
        super().__init__('test_image_publisher')
        self.declare_parameter('image_path', str(ASSETS / 'bus.jpg'))
        self.declare_parameter('rate_hz', 5.0)
        path = self.get_parameter('image_path').value
        frame = cv2.imread(path)
        if frame is None:
            raise RuntimeError(f'Could not read image: {path}')
        self.msg = bgr_to_msg(frame)
        self.pub = self.create_publisher(Image, '/camera/image_raw', 10)
        self.create_timer(1.0 / float(self.get_parameter('rate_hz').value), self._tick)
        self.get_logger().info(f'Publishing {path} on /camera/image_raw')

    def _tick(self):
        self.msg.header.stamp = self.get_clock().now().to_msg()
        self.pub.publish(self.msg)


def main(args=None):
    rclpy.init(args=args)
    node = TestImagePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
