#!/usr/bin/env bash
# runme.sh - run V2V, V2I, and sensors in multiple tmux panes

# Careful now
set -o errexit
set -o nounset

usage() {
  echo 'Usage: runme.sh [-i] [-d DELAY]'
  echo
  echo 'Run V2V, V2I, and sensors in multiple tmux panes.'
  echo
  echo 'Options:'
  echo
  echo '  -h, ?       Print this help text'
  echo '  -i          Run V2I as well as V2V'
  echo '  -d DELAY    Seconds to wait before spawning sensors, which'
  echo '              expect a vehicle to already be running.'
  echo '              (default: 4)'
  exit 1
}

while getopts d:ih f; do
  case "$f" in
    d) delay="${OPTARG}";;
    i) infra=true;;
    h | \?) usage;;
  esac
done
delay="${delay:-4}"

# DWIM (not what I say) venv creation and activation

if [ ! -d .venv ]; then
  echo 'No .venv directory found; creating'
  python3 -m venv .venv
  echo 'Activating .venv'
  . .venv/bin/activate
  echo 'Installing requirements in .venv'
  pip3 install -r requirements.txt
elif [ ! -x "$(command -v deactivate)" ]; then
  echo 'Activating .venv'
  . .venv/bin/activate
fi

# Fire the missiles

if [ -z "${infra:-}" ]; then
  # No infrastructure node: just a vehicle and its trusty sensors
  tmux new './code/peerTry.py'                                             \; \
       splitw    "sleep ${delay}; ./code/sensor.py --sensortype=speed"     \; \
       splitw -h   "sleep ${delay}; ./code/sensor.py --sensortype=longtitue" \; \
       selectp -L                                                           \; \
       splitw    "sleep ${delay}; ./code/sensor.py --sensortype=height"     \; \
       selectp -R     \; \
       splitw    "sleep ${delay}; ./code/sensor.py --sensortype=proximity" \; \
       selectp -R                      \; \
       splitw -h "sleep ${delay}; ./code/sensor.py --sensortype=heartrate" \; \
       splitw -h   "sleep ${delay}; ./code/sensor.py --sensortype=latitue"     \; \
       selectp -U                                                          \; \
       splitw -h "sleep ${delay}; ./code/sensor.py --sensortype=pressure"  \; \
       splitw -h "sleep ${delay}; ./code/sensor.py --sensortype=temperature"  \; \
       selectp -U                                                          \; \
       selectp-D                                                      \; \
       splitw -h "sleep ${delay}; ./code/sensor.py --sensortype=height" \; \
       selectp -U
else
  # Infrastructure and vehicle
  tmux new './code/infra.py'                                               \; \
       splitw -h './code/peerTry.py'                                       \; \
       splitw    "sleep ${delay}; ./code/sensor.py --sensortype=speed"     \; \
       splitw    "sleep ${delay}; ./code/sensor.py --sensortype=proximity" \; \
       selectp -L                                                          \; \
       splitw    "sleep ${delay}; ./code/sensor.py --sensortype=heartrate" \; \
       splitw    "sleep ${delay}; ./code/sensor.py --sensortype=pressure"
fi

# Be a good netizen

echo 'Deactivating .venv'
deactivate
