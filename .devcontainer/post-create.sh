#!/usr/bin/env bash
set -e
source /opt/ros/humble/setup.bash
sudo rosdep init 2>/dev/null || true
rosdep update
# The repository root is the ROS 2 package itself (package.xml at the root).
rosdep install --from-paths . --ignore-src -r -y
bash scripts/prepare_assets.sh
colcon build --symlink-install
echo "[ -f $PWD/install/setup.bash ] && source $PWD/install/setup.bash" >> ~/.bashrc
