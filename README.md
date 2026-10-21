# Лабораторна робота №7 — варіант 9
Інтеграція телеметрії та протоколу MAVLink. Виконала: Коман Аліна, ІР-33. Прийняв: Шихмат А. О.

**Параметри:** H = 35 м, V = 4 м/с (WP_SPD = 4 м/с ≡ WPNAV_SPEED = 400 см/с), ціль -35.3624857; 149.1642559.

**Середовище:** Ubuntu 22.04.5 (distrobox, x86_64; хост Debian 13), ROS 2 Humble, Gazebo Sim 8.15.0, ArduCopter V4.8.0-dev (a04e2c93), QGroundControl Daily.

## Структура
- `scripts/` — запуск і перевірка середовища (`start_env.sh`, `stop_env.sh`, `wait_ports.sh`, `check_env.sh`, `env.sh`)
- `mission/` — план місії `mission_variant9.plan` (Takeoff → Waypoint → Land)
- `telemetry/` — `.csv` і `.tlog` контрольного польоту
- `analysis/` — `analyze.py` (таблиця показників і 3 графіки з CSV)
- `results/` — графіки, `table_7_4.md`, звіт

## Запуск
```bash
distrobox enter ros2_humble
cd ~/fpv_labs && ./scripts/start_env.sh        # Gazebo + ArduPilot SITL + DDS
~/qgc/QGroundControl.AppImage                  # на хості
./scripts/check_env.sh                         # перевірка
```

## Аналіз телеметрії
```bash
pip install pandas numpy matplotlib
python3 analysis/analyze.py "telemetry/2026-10-21 23-01-13 vehicle1.csv"
```
