"""YOLOv8 target detection and tracking node with a search/patrol fallback.

Subscribes:
  /camera/image_raw   sensor_msgs/Image

Publishes:
  /cmd_vel            geometry_msgs/Twist         rotates to search, steers to track
  /detection          std_msgs/Float32MultiArray  [confidence, cx, cy, w, h, track_id,
                                                   latency_ms] of the best target
  /detection/image    sensor_msgs/Image           frame with boxes drawn on it
"""
import time

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import Float32MultiArray
from ultralytics import YOLO

from savunma_drone.image_utils import bgr_to_msg, msg_to_bgr


class TargetDetection(Node):

    def __init__(self):
        super().__init__('target_detection')
        self.declare_parameter('model', 'yolov8n.pt')
        self.declare_parameter('target_class', '')  # empty = any class
        self.declare_parameter('conf_threshold', 0.4)
        self.declare_parameter('image_size', 640)
        self.declare_parameter('search_angular_speed', 0.3)
        self.declare_parameter('kp', 0.8)
        self.declare_parameter('max_angular_speed', 0.6)
        self.declare_parameter('forward_speed', 0.0)
        self.declare_parameter('lost_timeout_s', 1.0)

        self.model = YOLO(self.get_parameter('model').value)
        self.conf = float(self.get_parameter('conf_threshold').value)
        self.imgsz = int(self.get_parameter('image_size').value)
        self.search_speed = float(self.get_parameter('search_angular_speed').value)
        self.kp = float(self.get_parameter('kp').value)
        self.max_speed = float(self.get_parameter('max_angular_speed').value)
        self.forward_speed = float(self.get_parameter('forward_speed').value)
        self.lost_timeout = float(self.get_parameter('lost_timeout_s').value)
        self.class_ids = self._resolve_classes(
            self.get_parameter('target_class').value)

        self.last_seen = None

        # Best-effort with a small queue: always process the newest frame.
        qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, depth=1)
        self.create_subscription(Image, '/camera/image_raw', self._on_image, qos)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.det_pub = self.create_publisher(Float32MultiArray, '/detection', 10)
        self.img_pub = self.create_publisher(Image, '/detection/image', 10)
        self.get_logger().info(
            f'Target detection started (classes: {self.class_ids or "all"})')

    def _resolve_classes(self, name):
        if not name:
            return None
        ids = [i for i, n in self.model.names.items() if n == name]
        if not ids:
            self.get_logger().warn(f'Unknown class "{name}", using all classes')
            return None
        return ids

    def _on_image(self, msg):
        frame = msg_to_bgr(msg)

        start = time.perf_counter()
        results = self.model.track(
            frame, persist=True, tracker='bytetrack.yaml', conf=self.conf, imgsz=self.imgsz,
            classes=self.class_ids, verbose=False)
        latency_ms = (time.perf_counter() - start) * 1000.0
        result = results[0]

        self.img_pub.publish(bgr_to_msg(result.plot(), msg.header))

        best = self._best_box(result)
        cmd = Twist()
        if best is not None:
            conf, cx, cy, w, h, track_id = best
            self.last_seen = time.monotonic()
            self.det_pub.publish(Float32MultiArray(
                data=[conf, cx, cy, w, h, track_id, latency_ms]))
            # Normalized horizontal error in [-1, 1]; positive = target on the right.
            error = (cx - frame.shape[1] / 2.0) / (frame.shape[1] / 2.0)
            cmd.angular.z = max(-self.max_speed, min(self.max_speed, -self.kp * error))
            cmd.linear.x = self.forward_speed
        elif self._target_lost():
            cmd.angular.z = self.search_speed  # search mode: rotate in place
        self.cmd_pub.publish(cmd)

    def _target_lost(self):
        if self.last_seen is None:
            return True
        return time.monotonic() - self.last_seen > self.lost_timeout

    @staticmethod
    def _best_box(result):
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            return None
        i = int(boxes.conf.argmax())
        cx, cy, w, h = (float(v) for v in boxes.xywh[i])
        track_id = float(boxes.id[i]) if boxes.id is not None else -1.0
        return float(boxes.conf[i]), cx, cy, w, h, track_id


def main(args=None):
    rclpy.init(args=args)
    node = TargetDetection()
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
