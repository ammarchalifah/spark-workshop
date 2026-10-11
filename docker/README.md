# Docker Cluster Setup

## Services

| Container | Hostname | Ports | Role |
|-----------|----------|-------|------|
| spark-master | spark-master | 8080, 7077 | Cluster master |
| spark-worker-1 | spark-worker-1 | 8081 | Executor node |
| spark-worker-2 | spark-worker-2 | 8082 | Executor node |
| jupyter-lab | jupyter-lab | 8888, 4040 | Notebooks + Spark driver |

## Commands

```bash
# From repo root
make build    # Build images
make up       # Start cluster
make down     # Stop cluster
make logs     # Follow logs
```

## Scaling Workers

```bash
docker compose -f docker/docker-compose.yml up -d --scale spark-worker-1=0 --scale spark-worker-2=0
docker compose -f docker/docker-compose.yml up -d --scale spark-worker=3
```

Note: The current compose file defines two named workers for predictable UI ports (8081, 8082). To scale beyond two, add additional worker service definitions or use a generic worker template.

## Gluten Profile (Module 06)

```bash
make up-gluten
```

Gluten requires manual download of the 1.7.0 Spark 4.1 binary. See [../06-java-gc-gluten/README.md](../06-java-gc-gluten/README.md).

## Troubleshooting

### Worker cannot connect to master

Ensure the master container is healthy before workers start. Check logs:

```bash
docker logs spark-master
docker logs spark-worker-1
```

### Jupyter cannot reach executors

The driver runs in client mode inside `jupyter-lab`. These settings are required:

- `spark.driver.host=jupyter-lab`
- `spark.driver.bindAddress=0.0.0.0`

Both are set in `spark-defaults.conf`.

### Permission errors on data volume

Output directories are created by entrypoint scripts. If you see permission issues, run:

```bash
make clean && make up
```

### Port already in use

Change host port mappings in `docker-compose.yml` if 8080, 8888, or 4040 are occupied.
