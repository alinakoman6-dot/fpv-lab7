#!/usr/bin/env bash
# Запуск симуляційного середовища: Gazebo + ArduPilot SITL + DDS (ROS 2).
# Використання:  ./scripts/start_env.sh [headless]
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/env.sh"
source_ros

"$DIR/stop_env.sh" quiet   # прибрати залишки попередніх запусків (порти!)
"$DIR/wait_ports.sh"

EXTRA=""
if [ "${1:-}" = "headless" ]; then
  EXTRA="gz_args:=-s -r"      # без вікна Gazebo (для серверів / Docker)
fi

echo "[start_env] ROS=$ROS_DISTRO ARDU_WS=$ARDU_WS launch=$LAUNCH_FILE"
nohup ros2 launch ardupilot_gz_bringup "$LAUNCH_FILE" rviz:=false $EXTRA \
  > "$LOG_DIR/sim.log" 2>&1 &
echo $! > "$LOG_DIR/sim.pid"
echo "[start_env] симулятор запущено (PID $(cat "$LOG_DIR/sim.pid")), лог: $LOG_DIR/sim.log"

echo "[start_env] чекаю на сервіси ArduPilot (до 180 с)..."
for i in $(seq 1 90); do
  if ros2 service list --no-daemon 2>/dev/null | grep -q "/ap/v1/arm_motors"; then
    echo "[start_env] ГОТОВО: сервіси ArduPilot доступні"
    exit 0
  fi
  sleep 2
done
echo "[start_env] ПОМИЛКА: сервіси не з'явились. Дивіться $LOG_DIR/sim.log"
exit 1
