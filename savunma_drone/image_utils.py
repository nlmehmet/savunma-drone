"""Image message helpers that do not depend on cv_bridge."""
import numpy as np
from sensor_msgs.msg import Image

_CHANNELS = {'bgr8': 3, 'rgb8': 3, 'bgra8': 4, 'rgba8': 4, 'mono8': 1}


def msg_to_bgr(msg):
    """Convert a sensor_msgs/Image to a BGR uint8 numpy array."""
    channels = _CHANNELS.get(msg.encoding)
    if channels is None:
        raise ValueError(f'Unsupported image encoding: {msg.encoding}')
    rows = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.step)
    img = rows[:, :msg.width * channels].reshape(msg.height, msg.width, channels)
    if msg.encoding == 'bgr8':
        return img.copy()
    if msg.encoding == 'rgb8':
        return img[:, :, ::-1].copy()
    if msg.encoding == 'bgra8':
        return img[:, :, :3].copy()
    if msg.encoding == 'rgba8':
        return img[:, :, 2::-1].copy()
    return np.repeat(img, 3, axis=2)  # mono8


def bgr_to_msg(frame, header=None):
    """Convert a BGR uint8 numpy array to a sensor_msgs/Image."""
    msg = Image()
    if header is not None:
        msg.header = header
    msg.height, msg.width = int(frame.shape[0]), int(frame.shape[1])
    msg.encoding = 'bgr8'
    msg.is_bigendian = 0
    msg.step = msg.width * 3
    msg.data = np.ascontiguousarray(frame, dtype=np.uint8).tobytes()
    return msg
