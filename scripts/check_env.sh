#!/usr/bin/env bash
# Перевірка, що середовище працює (запускати ПІСЛЯ start_env.sh).
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/env.sh"
source_ros
fail=0
ok()  { echo "  [OK]   $*"; }
bad() { echo "  [FAIL] $*"; fail=1; }

echo "== Версії =="
lsb_release -ds 2>/dev/null; uname -m
echo "ROS_DISTRO=$ROS_DISTRO"; gz sim --versions 2>/dev/null | head -1
python3 --version

echo "== Процеси =="
pgrep -f "gz sim|ign gazebo" >/dev/null && ok "Gazebo" || bad "Gazebo не запущено"
pgrep -f "arducopter" >/dev/null && ok "ArduPilot SITL (arducopter)" || bad "arducopter не запущено"

echo "== Сервіси ROS 2 =="
for s in /ap/v1/prearm_check /ap/v1/mode_switch /ap/v1/arm_motors \
         /ap/v1/experimental/takeoff; do
  ros2 service list --no-daemon 2>/dev/null | grep -qx "$s" && ok "$s" || bad "$s"
done

echo "== Теми ROS 2 =="
for t in /ap/v1/status /odometry /ap/v1/cmd_vel; do
  ros2 topic list --no-daemon 2>/dev/null | grep -qx "$t" && ok "$t" || bad "$t"
done
timeout 10 ros2 topic echo --once /odometry 2>/dev/null | grep -A3 "position:" \
  | head -4 && ok "одометрія надходить" || bad "одометрія не надходить"

echo "== Пакет =="
ros2 pkg executables fpv_lab2 2>/dev/null | grep -q flight_test \
  && ok "fpv_lab2 flight_test" || bad "пакет не зібраний (./scripts/build.sh)"
ros2 pkg executables fpv_lab2 2>/dev/null | grep -q fly_to_target \
  && ok "fpv_lab2 fly_to_target" || bad "fly_to_target відсутній"

[ $fail -eq 0 ] && echo "ВСЕ ГОТОВО" || echo "Є ПРОБЛЕМИ (див. FAIL вище)"
exit $fail
