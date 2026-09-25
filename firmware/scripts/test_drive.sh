#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
set -a
[ ! -f .env ] || . ./.env
[ ! -f .env.local ] || . ./.env.local
set +a

: "${ROBOT_HOST:?Set ROBOT_HOST in .env or the environment}"
: "${ROBOT_TOKEN:?Set ROBOT_TOKEN in .env or the environment}"

body_file=$(mktemp)
cleanup() {
    # Leave the robot stopped even if a request or assertion fails.
    curl --silent --max-time 5 -H "X-Robot-Token: $ROBOT_TOKEN" \
        "http://$ROBOT_HOST/stop" >/dev/null 2>&1 || true
    rm -f "$body_file"
}
trap cleanup EXIT

request() {
    label=$1
    path=$2
    expected=$3
    auth=$4
    printf '\n%s: GET %s\n' "$label" "$path"
    if [ "$auth" = token ]; then
        status=$(curl --silent --show-error --max-time 5 -o "$body_file" \
            -w '%{http_code}' -H "X-Robot-Token: $ROBOT_TOKEN" \
            "http://$ROBOT_HOST$path")
    else
        status=$(curl --silent --show-error --max-time 5 -o "$body_file" \
            -w '%{http_code}' "http://$ROBOT_HOST$path")
    fi
    cat "$body_file"
    printf '\nHTTP %s (expected %s)\n' "$status" "$expected"
    [ "$status" = "$expected" ] || exit 1
    sleep 0.5
}

request 'Health' '/health' 200 token
request 'Stopped drive' '/drive?left=0&right=0' 200 token
request 'Forward' '/drive?left=25&right=25' 200 token
request 'Stop' '/stop' 200 token
request 'Reverse' '/drive?left=-25&right=-25' 200 token
request 'Stop' '/stop' 200 token
request 'Turn left' '/drive?left=-25&right=25' 200 token
request 'Stop' '/stop' 200 token
request 'Turn right' '/drive?left=25&right=-25' 200 token
request 'Stop' '/stop' 200 token
request 'Uneven speed' '/drive?left=10&right=30' 200 token
request 'Stop' '/stop' 200 token

request 'Missing right' '/drive?left=10' 400 token
request 'Missing left' '/drive?right=10' 400 token
request 'Non-numeric speed' '/drive?left=fast&right=10' 400 token
request 'Too high' '/drive?left=101&right=0' 400 token
request 'Too low' '/drive?left=0&right=-101' 400 token
request 'Unknown route' '/missing' 404 token
request 'Missing token' '/health' 403 no-token
request 'Health again' '/health' 200 token
