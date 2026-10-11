.PHONY: setup up down logs cache-data build clean

COMPOSE = docker compose -f docker/docker-compose.yml
COMPOSE_GLUTEN = docker compose -f docker/docker-compose.yml -f docker/docker-compose.gluten.yml

setup:
	@echo "Creating Python virtual environment..."
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements/requirements.txt
	@echo "Setup complete. Run 'make up' to start the cluster."

build:
	$(COMPOSE) build

up: build
	$(COMPOSE) up -d
	@echo ""
	@echo "Workshop cluster is starting."
	@echo "  Jupyter Lab:  http://localhost:8888"
	@echo "  Spark Master: http://localhost:8080"
	@echo "  Spark App UI: http://localhost:4040 (after running a notebook)"
	@echo ""
	@echo "Run 'make logs' to follow startup output."

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

cache-data:
	@mkdir -p data/cache
	@echo "Downloading NYC TLC workshop datasets..."
	curl -fL -o data/cache/yellow_tripdata_2024-01.parquet \
		"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
	curl -fL -o data/cache/yellow_tripdata_2024-02.parquet \
		"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-02.parquet"
	curl -fL -o data/cache/taxi_zone_lookup.csv \
		"https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
	@echo "Cached datasets in data/cache/"

up-gluten:
	$(COMPOSE_GLUTEN) --profile gluten up -d
	@echo "Gluten profile started. See 06-java-gc-gluten/README.md for usage."

clean:
	$(COMPOSE) down -v
	rm -rf data/output data/cache
