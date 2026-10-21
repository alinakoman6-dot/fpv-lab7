#!/usr/bin/env bash
# Чекає, поки TCP-порт 5760 (SITL) повністю звільниться після зупинки.
busy() { awk 'toupper($2) ~ /:1680$/ {f=1} END{exit !f}' /proc/net/tcp /proc/net/tcp6 2>/dev/null; }
for i in $(seq 1 120); do
  busy || { echo "[wait_ports] порт 5760 вільний"; exit 0; }
  [ $((i % 10)) -eq 1 ] && echo "[wait_ports] порт 5760 ще зайнятий, чекаю..."
  sleep 1
done
echo "[wait_ports] порт 5760 так і не звільнився"; exit 1
