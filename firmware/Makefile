flash-id:
	uv run esptool flash-id

erase-flash:
	uv run esptool erase_flash

write-flash:
	uv run esptool --baud 460800 write_flash 0 ESP32_GENERIC_S3-20260824-v1.29.0.bin

list:
	uv run mpremote connect list

cp:
	uv run mpremote cp $(or $(word 2,$(MAKECMDGOALS)),main.py) :$(or $(word 2,$(MAKECMDGOALS)),main.py)

ls:
	uv run mpremote ls $(or $(word 2,$(MAKECMDGOALS)),)

repl:
	uv run mpremote repl

mkdir:
	uv run mpremote mkdir $(or $(word 2,$(MAKECMDGOALS)),src)

reset:
	uv run mpremote reset

env:
	@set -a; [ -f .env ] && . .env; [ -f .env.local ] && . .env.local; set +a

webrepl:
	@test -n "$(ROBOT_HOST)" || (echo "Set ROBOT_HOST to the robot's IP"; exit 1)
	@test -n "$(WEBREPL_PASSWORD)" || (echo "Set WEBREPL_PASSWORD in .env or the environment"; exit 1)
	@test -n "$(ROBOT_TOKEN)" || (echo "Set ROBOT_TOKEN to CONTROL_TOKEN from wifi_config.py"; exit 1)
	uv run tools/webrepl/webrepl_cli.py --help
# 	uv run tools/webrepl/webrepl_cli.py $(ROBOT_HOST) # slow

webrepl-cp:
	uv run tools/webrepl/webrepl_cli.py -p $(WEBREPL_PASSWORD) $(word 2,$(MAKECMDGOALS)) $(ROBOT_HOST):$(word 2,$(MAKECMDGOALS))

restart:
	@echo "Restarting robot"
	@curl --fail --show-error --silent --max-time 5 -H "X-Robot-Token: $(ROBOT_TOKEN)" "http://$(ROBOT_HOST)/reset"

health:
	@curl --fail --show-error --silent --max-time 5 -H "X-Robot-Token: $(ROBOT_TOKEN)" "http://$(ROBOT_HOST)/health"

LOG_PORT ?= 9999

logs:
	uv run scripts/logs.py --port $(LOG_PORT)

test-endpoints:
	@sh scripts/test_endpoints.sh

test-drive:
	@sh scripts/test_drive.sh

test-watchdog:
	@sh scripts/test_watchdog.sh

test:
	env -u VIRTUAL_ENV uv run python -m pytest tests/
