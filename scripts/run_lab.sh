#!/usr/bin/env bash
# Запуск польотів і збереження журналів.
#   ./scripts/run_lab.sh example   - початковий приклад (зліт-зависання-посадка)
#   ./scripts/run_lab.sh target    - політ до цілі, ВАРІАНТ 9 (dx=5.2, dy=-0.1)
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/env.sh"
source_ros
STAMP="$(date +%Y%m%d_%H%M%S)"

case "${1:-target}" in
  example)
    ros2 run fpv_lab2 flight_test 2>&1 | tee "$LOG_DIR/example_$STAMP.log" ;;
  target)
    ros2 run fpv_lab2 fly_to_target --ros-args \
      -p delta_x:=5.2 -p delta_y:=-0.1 2>&1 \
      | tee "$LOG_DIR/target_$STAMP.log" ;;
  *) echo "Використання: $0 example|target"; exit 2 ;;
esac
