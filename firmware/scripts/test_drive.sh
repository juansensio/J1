#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
set -a
[ ! -f .env ] || . ./.env
[ ! -f .env.local ] || . ./.env.local
set +a

: "${ROBOT_HOST:?Set ROBOT_HOST in .env or the environment}"
: "${ROBOT_TOKEN:?Set ROBOT_TOKEN in .env or the environment}"

left_speed=0
right_speed=0
stopped=0

stop_robot() {
    curl --fail --silent --show-error --max-time 5 -o /dev/null \
        -H "X-Robot-Token: $ROBOT_TOKEN" "http://$ROBOT_HOST/stop"
}

cleanup() {
    if [ "$stopped" -eq 0 ]; then
        stop_robot || true
    fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

drive() {
    printf 'left=%s right=%s\n' "$1" "$2"
    curl --fail --silent --show-error --max-time 5 -o /dev/null \
        -H "X-Robot-Token: $ROBOT_TOKEN" \
        "http://$ROBOT_HOST/drive?left=$1&right=$2"
}

step_toward() {
    current=$1
    target=$2
    if [ "$current" -lt "$target" ]; then
        current=$((current + 5))
        [ "$current" -le "$target" ] || current=$target
    elif [ "$current" -gt "$target" ]; then
        current=$((current - 5))
        [ "$current" -ge "$target" ] || current=$target
    fi
    printf '%s\n' "$current"
}

ramp_to() {
    target_left=$1
    target_right=$2
    while [ "$left_speed" -ne "$target_left" ] || \
          [ "$right_speed" -ne "$target_right" ]; do
        left_speed=$(step_toward "$left_speed" "$target_left")
        right_speed=$(step_toward "$right_speed" "$target_right")
        drive "$left_speed" "$right_speed"
        sleep 0.12
    done
}

printf '\nForward\n'
ramp_to 80 80
sleep 0.35
ramp_to 0 0
sleep 0.25

printf '\nBackward\n'
ramp_to -80 -80
sleep 0.35
ramp_to 0 0
sleep 0.25

printf '\nTurn left\n'
ramp_to -80 80
sleep 0.4
ramp_to 0 0
sleep 0.25

printf '\nTurn right\n'
ramp_to 80 -80
sleep 0.4
ramp_to 0 0

printf '\nStop\n'
stop_robot
stopped=1
