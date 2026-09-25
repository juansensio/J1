build:
	docker compose build

run:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

bash:
	docker exec -it ros2-jazzy zsh -c "\
		source /opt/ros/jazzy/setup.zsh && \
		cd /root/ros2_ws && \
		source install/setup.zsh && \
		exec zsh \
	"

test:
	PYTHONPATH=ros2_ws/src/bridge .venv/bin/python -m pytest -q ros2_ws/src/bridge/test/test_kinematics.py ros2_ws/src/bridge/test/test_bridge.py
