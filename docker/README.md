# Docker cluster

## Services

| Container | Hostname | Ports | Role |
|-----------|----------|-------|------|
| spark-master | spark-master | 8080, 7077 | Cluster master |
| spark-worker-1 | spark-worker-1 | 8081 | Executor node |
| spark-worker-2 | spark-worker-2 | 8082 | Executor node |
| jupyter-lab | jupyter-lab | 8888, 4040 | Notebooks + Spark driver |

## Commands

From the repository root:

```bash
./scripts/cluster-up.sh
./scripts/cluster-down.sh
./scripts/cluster-logs.sh
```

Or use Compose directly:

```bash
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml up -d
docker compose -f docker/docker-compose.yml down
docker compose -f docker/docker-compose.yml logs -f
```

## Scaling workers

The compose file defines two named workers so UI ports stay at 8081 and 8082. To change capacity, edit `docker-compose.yml` or add worker service definitions.

## Troubleshooting

### Worker cannot connect to master

Wait for the master to be healthy:

```bash
docker logs spark-master
docker logs spark-worker-1
```

### Jupyter cannot reach executors

The driver runs in client mode inside `jupyter-lab`. Required settings (in `spark-defaults.conf`):

- `spark.driver.host=jupyter-lab`
- `spark.driver.bindAddress=0.0.0.0`

### Permission errors on `data/output`

Recreate after `entrypoint-init.sh` runs:

```bash
./scripts/cluster-down.sh
docker compose -f docker/docker-compose.yml down -v
./scripts/cluster-up.sh
```

### Port already in use

Change host port mappings in `docker-compose.yml` if 8080, 8888, or 4040 conflict.
