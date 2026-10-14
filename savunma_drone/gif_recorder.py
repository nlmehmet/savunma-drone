"""Records /detection/image (camera frames with detection boxes) into an animated GIF.

Usage:
    ros2 run savunma_drone gif_recorder --ros-args -p duration_s:=40.0 -p output:=docs/demo.gif
"""
import os
import time

from PIL import Image as PILImage
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

from savunma_drone.image_utils import msg_to_bgr


def save_gif(frames, path, fps):
    """Save a list of PIL images as a looping GIF."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    frames[0].save(
        path, save_all=True, append_images=frames[1:],
        duration=int(1000 / fps), loop=0, optimize=True)


class GifRecorder(Node):

    def __init__(self):
        super().__init__('gif_recorder')
        self.declare_parameter('output', 'docs/demo.gif')
        self.declare_parameter('duration_s', 40.0)
        self.declare_parameter('fps', 3.0)
        self.declare_parameter('width', 400)
        self.output = self.get_parameter('output').value
        self.duration = float(self.get_parameter('duration_s').value)
        self.fps = float(self.get_parameter('fps').value)
        self.width = int(self.get_parameter('width').value)

        self.frames = []
        self.start = None
        self.last = 0.0
        self.create_subscription(Image, '/detection/image', self._on_image, 10)
        self.get_logger().info(
            f'Waiting for frames on /detection/image, recording {self.duration:.0f} s')

    def finished(self):
        return self.start is not None and time.monotonic() - self.start >= self.duration

    def _on_image(self, msg):
        now = time.monotonic()
        if self.start is None:
            self.start = now
            self.get_logger().info('Recording started')
        if now - self.last < 1.0 / self.fps or self.finished():
            return
        self.last = now
        rgb = msg_to_bgr(msg)[:, :, ::-1]
        img = PILImage.fromarray(rgb)
        height = int(img.height * self.width / img.width)
        self.frames.append(img.resize((self.width, height)))

    def save(self):
        if not self.frames:
            self.get_logger().error('No frames received, nothing saved')
            return
        save_gif(self.frames, self.output, self.fps)
        size_mb = os.path.getsize(self.output) / 1e6
        self.get_logger().info(
            f'Saved {len(self.frames)} frames to {self.output} ({size_mb:.1f} MB)')


def main(args=None):
    rclpy.init(args=args)
    node = GifRecorder()
    try:
        while rclpy.ok() and not node.finished():
            rclpy.spin_once(node, timeout_sec=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        node.save()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
