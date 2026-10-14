import os

from setuptools import find_packages, setup

package_name = 'savunma_drone'


def collect(source_dir):
    """Install a whole directory tree under share/<package>/<source_dir>."""
    entries = []
    for root, _, files in os.walk(source_dir):
        if files:
            target = os.path.join('share', package_name, root)
            entries.append((target, [os.path.join(root, f) for f in files]))
    return entries


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ] + collect('launch') + collect('worlds') + collect('models'),
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='ROS 2 autonomous surveillance simulation with data logging',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'data_recorder = savunma_drone.data_recorder:main',
            'target_detection = savunma_drone.target_detection:main',
            'test_image_publisher = savunma_drone.test_image_publisher:main',
            'gif_recorder = savunma_drone.gif_recorder:main',
        ],
    },
)
