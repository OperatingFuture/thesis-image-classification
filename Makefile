help:
	@echo "Usage: make [option]"
	@echo "OPTIONS:"
	@echo "  run       		 use to run the project locally (via docker-compose)."
	@echo "  run-detached    use to run the project locally (via docker-compose) in detached mode."


run:
	docker compose down -v
	docker compose up -d

run-clean:
	docker compose down -v
	docker compose up  --build

run-detached:
	docker compose down -v
	docker compose up -d --build

down:
	docker compose down -v