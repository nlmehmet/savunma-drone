# ROS 2 Autonomous Surveillance System (Defense Robotics Simulation)

This project implements a closed-loop autonomy and target search algorithm for unmanned ground/air vehicles using **ROS 2 Humble**, **Gazebo**, **OpenCV**, and **Python**. Developed as part of robotics and artificial intelligence studies.

> GIF: (a recording of the drone detecting and tracking a target in Gazebo will be added here)

## Features

- **Simulation Environment:** Gazebo SITL integration with sensor suites.
- **Computer Vision Pipeline:** Real-time camera stream parsing via `cv_bridge` and OpenCV matrix transformations.
- **Autonomous Search/Patrol Mode:** Closed-loop velocity commands (`geometry_msgs/Twist`) allowing the robot to execute automated patrol routines when targets are out of sight.
- **ROS 2 Node Architecture:** Modular design separating sensor subscription and motor actuation.
- **Run Data Logging:** The `data_recorder` node logs position, velocity, commands and detections to CSV for later analysis.

## Tech Stack

- **Framework:** ROS 2 Humble
- **Physics Simulator:** Gazebo
- **Language:** Python (rclpy, OpenCV)
- **Message Types:** `sensor_msgs/Image`, `geometry_msgs/Twist`, `nav_msgs/Odometry`

## Quick Start (GitHub Codespaces)

1. Go to **Code > Codespaces > Create codespace on main** (4 cores recommended).
2. When the setup finishes, the package is already built (`colcon build --symlink-install`).
3. Open port **6080** to see the Gazebo desktop in your browser (noVNC, default password: `vscode`).
4. Start the data recorder: `ros2 run savunma_drone data_recorder`

## Roadmap

- [x] Basic ROS 2 + Gazebo simulation with patrol mode
- [ ] Codespaces development environment (devcontainer)
- [ ] YOLOv8 target detection node + yaw/pitch tracking
- [ ] Run data logging and analysis (pandas, Plotly, Streamlit dashboard)
- [ ] Demo GIF + architecture diagram
- [ ] PX4 SITL + MicroXRCE-DDS (Offboard control)
- [ ] Gimbal payload design (Autodesk Inventor)

## Architecture

`camera -> /camera/image_raw -> target detection (YOLOv8) -> /detection -> control -> /cmd_vel`

Run data is recorded to `data/runs/*.csv` and analyzed in `analysis/`.
