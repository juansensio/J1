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