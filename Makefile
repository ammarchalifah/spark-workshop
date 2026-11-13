# Optional convenience targets for macOS/Linux (Make is not required — see README).
.PHONY: up down logs cache-data build clean

COMPOSE = docker compose -f docker/docker-compose.yml

build:
	$(COMPOSE) build

up:
	@./scripts/cluster-up.sh

down:
	@./scripts/cluster-down.sh

logs:
	@./scripts/cluster-logs.sh

cache-data:
	@./scripts/cache-data.sh

clean:
	@./scripts/cluster-clean.sh
