build:
	docker compose build

run:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose exec -T ros2-jazzy sh -c 'mkdir -p /root/ros2_ws/log/client && touch /root/ros2_ws/log/client/bridge.log && tail -n 60 -F /root/ros2_ws/log/client/bridge.log'

bash:
	docker exec -it ros2-jazzy zsh -c "\
		source /opt/ros/jazzy/setup.zsh && \
		cd /root/ros2_ws && \
		source install/setup.zsh && \
		exec zsh \
	"

test:
	PYTHONPATH=ros2_ws/src/bridge .venv/bin/python -m pytest -q ros2_ws/src/bridge/test

client: run
	@docker compose exec -T ros2-jazzy python3 -c 'import socket; socket.create_connection(("127.0.0.1", 8080), 1).close()' >/dev/null 2>&1 || docker compose exec -d ros2-jazzy python3 -m http.server 8080 --bind 0.0.0.0 --directory /root/web
	@echo 'Robot client on this Mac: http://localhost:8080'
	@LAN_IP=$$(ifconfig en0 | awk '/inet / { print $$2; exit }'); if [ -n "$$LAN_IP" ]; then echo "Robot client on your phone: http://$$LAN_IP:8080"; fi
	@echo 'Start the ROS-to-ESP32 bridge separately: make bridge'

bridge: run
	@docker compose exec -T ros2-jazzy bash -lc 'source /opt/ros/jazzy/setup.bash && cd /root/ros2_ws && colcon build --packages-select bridge'
	@docker compose exec -T ros2-jazzy sh -c 'mkdir -p /root/ros2_ws/log/client && touch /root/ros2_ws/log/client/bridge.log'
	@docker compose exec -T ros2-jazzy python3 -c 'import socket; socket.create_connection(("127.0.0.1", 9090), 1).close()' >/dev/null 2>&1 || docker compose exec -d ros2-jazzy bash -lc 'source /opt/ros/jazzy/setup.bash && exec ros2 launch rosbridge_server rosbridge_websocket_launch.xml'
	@docker compose exec -T ros2-jazzy bash -lc 'source /opt/ros/jazzy/setup.bash && source /root/ros2_ws/install/setup.bash && ros2 node list | grep -Fx /bridge' >/dev/null 2>&1 || docker compose exec -d ros2-jazzy bash -lc 'source /opt/ros/jazzy/setup.bash && source /root/ros2_ws/install/setup.bash && exec ros2 run bridge bridge --ros-args -p robot_host:="$$ROBOT_HOST" -p robot_token:="$$ROBOT_TOKEN" >> /root/ros2_ws/log/client/bridge.log 2>&1'
	@echo 'ROS-to-ESP32 bridge started (or already running).'
	@echo 'Live bridge logs: make logs'
