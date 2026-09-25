LOG_PORT ?= 9999

logs:
	uv run scripts/logs.py --port $(LOG_PORT)

test:
	env -u VIRTUAL_ENV uv run python -m pytest tests/
	cd firmware && env -u VIRTUAL_ENV uv run python -m pytest tests/
