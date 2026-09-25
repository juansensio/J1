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