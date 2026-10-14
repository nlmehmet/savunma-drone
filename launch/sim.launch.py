"""Start Gazebo with the target-search world, the detection node and the recorder."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.actions import SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('savunma_drone')
    gazebo_share = get_package_share_directory('gazebo_ros')

    return LaunchDescription([
        DeclareLaunchArgument(
            'world', default_value=os.path.join(share, 'worlds', 'target_search.world')),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('record_data', default_value='true'),
        DeclareLaunchArgument('target_class', default_value='person'),

        SetEnvironmentVariable(
            'GAZEBO_MODEL_PATH',
            [os.path.join(share, 'models'), ':',
             EnvironmentVariable('GAZEBO_MODEL_PATH', default_value='')]),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gazebo_share, 'launch', 'gazebo.launch.py')),
            launch_arguments={
                'world': LaunchConfiguration('world'),
                'gui': LaunchConfiguration('gui'),
            }.items()),

        Node(
            package='savunma_drone', executable='target_detection',
            output='screen',
            parameters=[{'target_class': LaunchConfiguration('target_class')}]),

        Node(
            package='savunma_drone', executable='data_recorder',
            output='screen', condition=IfCondition(LaunchConfiguration('record_data'))),
    ])
