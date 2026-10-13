"""Logs simulation data to a CSV file at a fixed rate.

Subscribed topics:
  /odom        nav_msgs/Odometry           drone position and velocity
  /cmd_vel     geometry_msgs/Twist         commanded velocity
  /detection   std_msgs/Float32MultiArray  [confidence, cx, cy, w, h, track_id, latency_ms]
               (published by the YOLOv8 detection node in this format)
"""
import csv
from datetime import datetime
import os

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

HEADER = [
    't', 'x', 'y', 'z', 'vx', 'vy', 'vz',
    'cmd_lin_x', 'cmd_ang_z',
    'detected', 'confidence', 'cx', 'cy', 'w', 'h', 'track_id', 'latency_ms',
]
DETECTION_TIMEOUT_S = 0.5


class DataRecorder(Node):

    def __init__(self):
        super().__init__('data_recorder')
        self.declare_parameter('output_dir', 'data/runs')
        self.declare_parameter('rate_hz', 10.0)
        output_dir = self.get_parameter('output_dir').value
        rate_hz = float(self.get_parameter('rate_hz').value)

        self.odom = None
        self.cmd = None
        self.detection = None
        self.detection_time = None

        self.create_subscription(Odometry, '/odom', self._odom_cb, 10)
        self.create_subscription(Twist, '/cmd_vel', self._cmd_cb, 10)
        self.create_subscription(
            Float32MultiArray, '/detection', self._detection_cb, 10)

        os.makedirs(output_dir, exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.path = os.path.join(output_dir, f'run_{stamp}.csv')
        self.file = open(self.path, 'w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(HEADER)

        self.start_time = self.get_clock().now()
        self.create_timer(1.0 / rate_hz, self._write_row)
        self.get_logger().info(f'Recording started: {self.path}')

    def _odom_cb(self, msg):
        self.odom = msg

    def _cmd_cb(self, msg):
        self.cmd = msg

    def _detection_cb(self, msg):
        if len(msg.data) >= 7:
            self.detection = list(msg.data[:7])
            self.detection_time = self.get_clock().now()

    def _write_row(self):
        now = self.get_clock().now()
        t = (now - self.start_time).nanoseconds / 1e9

        if self.odom:
            p = self.odom.pose.pose.position
            v = self.odom.twist.twist.linear
            state = [p.x, p.y, p.z, v.x, v.y, v.z]
        else:
            state = [''] * 6

        if self.cmd:
            cmd = [self.cmd.linear.x, self.cmd.angular.z]
        else:
            cmd = ['', '']

        fresh = (
            self.detection is not None
            and (now - self.detection_time).nanoseconds / 1e9
            < DETECTION_TIMEOUT_S
        )
        detection = [1] + self.detection if fresh else [0] + [''] * 7

        self.writer.writerow([round(t, 3)] + state + cmd + detection)
        self.file.flush()

    def destroy_node(self):
        self.file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = DataRecorder()
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
