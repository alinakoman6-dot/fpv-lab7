#!/usr/bin/env bash
# Зупинка всіх компонентів симуляції (звільняє порти для повторного запуску).
QUIET="${1:-}"
say() { [ "$QUIET" = "quiet" ] || echo "[stop_env] $*"; }

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="$DIR/../logs/sim.pid"
if [ -f "$PIDFILE" ]; then
  kill -INT "$(cat "$PIDFILE")" 2>/dev/null
  sleep 2
  rm -f "$PIDFILE"
fi

# Лише процеси, пов'язані з симуляцією (без чужих файлів і системних команд)
for p in "gz sim" "ign gazebo" "ruby.*gz" "arducopter" "micro_ros_agent" "MicroXRCEAgent" "mavproxy" \
         "sim_vehicle.py" "ardupilot_gz"; do
  pkill -f "$p" 2>/dev/null && say "завершено: $p"
done
sleep 5
say "готово"
exit 0
