import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2

class OtonomSistem(Node):
    def __init__(self):
        super().__init__('otonom_sistem')
        self.subscription = self.create_subscription(
            Image, '/camera/image_raw', self.kamera_callback, 10)
        self.bridge = CvBridge()
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info("Otonom Devriye (Arama Modu) Başlatıldı!")

    def kamera_callback(self, data):
        frame = self.bridge.imgmsg_to_cv2(data, "bgr8")
        hiz_komutu = Twist()
        hiz_komutu.linear.x = 0.0
        hiz_komutu.angular.z = 0.3
        self.publisher.publish(hiz_komutu)
        self.get_logger().info("Hedef aranıyor... Araç kendi etrafında dönüyor.")

def main(args=None):
    rclpy.init(args=args)
    otonom_node = OtonomSistem()
    rclpy.spin(otonom_node)
    otonom_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
