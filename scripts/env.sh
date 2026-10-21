#!/usr/bin/env bash
# Спільні змінні. За потреби змініть шляхи під свою систему.
export ROS_DISTRO="${ROS_DISTRO:-humble}"
export ARDU_WS="${ARDU_WS:-/opt/ardu_ws}"            # робочий простір ArduPilot
export LAB_WS="${LAB_WS:-$HOME/fpv_labs}"            # цей робочий простір
export LAUNCH_FILE="${LAUNCH_FILE:-iris_maze.launch.py}"  # світ maze.sdf
export LOG_DIR="$LAB_WS/logs"
mkdir -p "$LOG_DIR"

source_ros() {
  # shellcheck disable=SC1090
  source "/opt/ros/$ROS_DISTRO/setup.bash"
  [ -f "$ARDU_WS/install/setup.bash" ] && source "$ARDU_WS/install/setup.bash"
  [ -f "$LAB_WS/install/setup.bash" ] && source "$LAB_WS/install/setup.bash"
  return 0
}
export LIBGL_ALWAYS_SOFTWARE=1
export LP_NUM_THREADS=2
export GZ_SIM_RESOURCE_PATH="$ARDU_WS/install/ardupilot_gazebo/share:$GZ_SIM_RESOURCE_PATH"
