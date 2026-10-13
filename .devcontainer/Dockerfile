FROM osrf/ros:humble-desktop

ARG USERNAME=ros
ARG UID=1000
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo git curl python3-pip python3-colcon-common-extensions python3-rosdep \
    ros-humble-gazebo-ros-pkgs ros-humble-cv-bridge ros-humble-vision-opencv \
    ros-humble-rqt-image-view \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u ${UID} -s /bin/bash ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME}

# CPU-only PyTorch + YOLOv8 (Codespaces has no GPU). cv_bridge requires numpy<2.
RUN pip3 install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip3 install --no-cache-dir ultralytics \
    && pip3 install --no-cache-dir pandas matplotlib plotly streamlit \
    && pip3 install --no-cache-dir "numpy<2"

USER ${USERNAME}
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
