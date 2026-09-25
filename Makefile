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

client: run
	@docker compose exec -T ros2-jazzy python3 -c 'import socket; socket.create_connection(("127.0.0.1", 9090), 1).close()' >/dev/null 2>&1 || docker compose exec -d ros2-jazzy bash -lc 'source /opt/ros/jazzy/setup.bash && exec ros2 launch rosbridge_server rosbridge_websocket_launch.xml'
	@docker compose exec -T ros2-jazzy python3 -c 'import socket; socket.create_connection(("127.0.0.1", 8080), 1).close()' >/dev/null 2>&1 || docker compose exec -d ros2-jazzy python3 -m http.server 8080 --bind 0.0.0.0 --directory /root/web
	@echo 'Web client: http://localhost:8080 (or http://MAC_LAN_IP:8080 from your phone)'
