#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
set -a
[ ! -f .env ] || . ./.env
[ ! -f .env.local ] || . ./.env.local
set +a

: "${ROBOT_HOST:?Set ROBOT_HOST in .env or the environment}"
: "${ROBOT_TOKEN:?Set ROBOT_TOKEN in .env or the environment}"

stop_robot() {
    curl --silent --max-time 5 -H "X-Robot-Token: $ROBOT_TOKEN" \
        "http://$ROBOT_HOST/stop" >/dev/null 2>&1 || true
}
trap stop_robot EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

printf 'Sending one drive command, then waiting without sending another...\n'
curl --fail --silent --show-error --max-time 5 -o /dev/null \
    -H "X-Robot-Token: $ROBOT_TOKEN" \
    "http://$ROBOT_HOST/drive?left=30&right=30"

sleep 1.2
printf 'The log should now show "Drive watchdog expired" and "Drive stopped".\n'
curl --fail --silent --show-error --max-time 5 -o /dev/null \
    -H "X-Robot-Token: $ROBOT_TOKEN" "http://$ROBOT_HOST/health"
