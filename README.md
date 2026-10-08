# ROS 2 Autonomous Surveillance System (Defense Robotics Simulation)

This project implements a closed-loop autonomy and target search algorithm for unmanned ground/air vehicles using **ROS 2 Humble**, **Gazebo**, **OpenCV**, and **Python**. Developed as part of robotics and artificial intelligence studies.

## 🚀 Features
- **Simulation Environment:** Gazebo SITL integration with sensor suites.
- **Computer Vision Pipeline:** Real-time camera stream parsing via `cv_bridge` and OpenCV matrix transformations.
- **Autonomous Search/Patrol Mode:** Closed-loop velocity commands (`geometry_msgs/Twist`) allowing the robot to execute automated patrol routines when targets are out of sight.
- **ROS 2 Node Architecture:** Modular design separating sensor subscription and motor actuation.

## 🛠️ Tech Stack
- **Framework:** ROS 2 Humble
- **Physics Simulator:** Gazebo
- **Language:** Python (rclpy, OpenCV)
- **Message Types:** `sensor_msgs/Image`, `geometry_msgs/Twist`

## 📂 Code Structure
## ⚙️ How to Run
1. Launch the Gazebo simulation environment with the robot model.
2. Build the workspace using `colcon build`.
3. Run the autonomy node:
