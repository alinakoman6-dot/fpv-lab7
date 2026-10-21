#!/usr/bin/env bash
# Складання пакета fpv_lab2.
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/env.sh"
source "/opt/ros/$ROS_DISTRO/setup.bash"
source "$ARDU_WS/install/setup.bash"
cd "$LAB_WS"
colcon build --symlink-install --packages-select fpv_lab2
source "$LAB_WS/install/setup.bash"
echo "--- виконувані вузли пакета:"
ros2 pkg executables fpv_lab2
