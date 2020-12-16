#!/usr/bin/env bash
# launch-tmux.sh - run V2V, V2I, and sensors in multiple tmux panes

set -o errexit
set -o nounset

usage() {
  echo 'Usage: launch-tmux [-i]'
  echo
  echo 'Run V2V, V2I, and sensors in multiple tmux panes.'
  echo
  echo 'Options:'
  echo
  echo '  -h, ?       Print this help text'
  echo '  -i          Run V2I as well as V2v'
  exit 1
}

while getopts ih f; do
  case "$f" in
    i) infra=true;;
    h | \?) usage;;
  esac
done

. .venv/bin/activate
if [ -z "${infra:-}" ]; then
  tmux new 'python code/peerTry.py'                                 \; \
       splitw -h 'sleep 4; ./code/sensor.py --sensortype=speed'     \; \
       splitw    'sleep 4; ./code/sensor.py --sensortype=proximity' \; \
       selectp -L                                                   \; \
       splitw    'sleep 4; ./code/sensor.py --sensortype=heartrate' \; \
       splitw    'sleep 4; ./code/sensor.py --sensortype=pressure'
else
  tmux new './code/infra.py'                                        \; \
       splitw -h 'python code/peerTry.py'                           \; \
       splitw    'sleep 4; ./code/sensor.py --sensortype=speed'     \; \
       splitw    'sleep 4; ./code/sensor.py --sensortype=proximity' \; \
       selectp -L                                                   \; \
       splitw    'sleep 4; ./code/sensor.py --sensortype=heartrate' \; \
       splitw    'sleep 4; ./code/sensor.py --sensortype=pressure'
fi
