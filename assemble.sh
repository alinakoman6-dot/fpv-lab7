#!/usr/bin/env bash
# Збирає готову теку лабораторної з файлів на твоєму комп'ютері.
# Використання (з теки fpv-lab7):  ./assemble.sh [шлях/до/звіту.pdf]
set -u
cd "$(dirname "$0")"
SCRIPTS_SRC="$HOME/fpv_labs/scripts"
TEL_SRC="$HOME/lab7_logs/Telemetry"
CSV="2026-10-21 23-01-13 vehicle1.csv"

echo "== scripts =="
cp -v "$SCRIPTS_SRC"/*.sh scripts/ 2>/dev/null || echo "!! не знайдено $SCRIPTS_SRC"

echo "== telemetry =="
if [ -f "$TEL_SRC/$CSV" ]; then cp -v "$TEL_SRC/$CSV" telemetry/; else echo "!! немає $TEL_SRC/$CSV"; fi
TLOG=$(ls -t "$TEL_SRC"/2026-10-21\ 23-*.tlog 2>/dev/null | head -1)
if [ -n "$TLOG" ]; then cp -v "$TLOG" telemetry/; else
  echo "!! .tlog для польоту 23:xx не знайдено (закрий QGC і перевір теку Telemetry)"; fi

echo "== analysis =="
python3 analysis/analyze.py "telemetry/$CSV" || echo "!! аналіз не вдався — надішли вивід Claude"

echo "== report =="
if [ "${1:-}" ] && [ -f "$1" ]; then cp -v "$1" results/; else echo "(звіт не вказано: ./assemble.sh ~/шлях/звіт.pdf)"; fi

echo; echo "Готово. Вміст:"; ls -R . | head -40
