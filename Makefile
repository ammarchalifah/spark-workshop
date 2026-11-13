# Optional shortcuts (GNU Make not required — see README).
.PHONY: up down logs build clean

COMPOSE = docker compose -f docker/docker-compose.yml

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

clean:
	$(COMPOSE) down -v
	rm -rf data/output data/cache
