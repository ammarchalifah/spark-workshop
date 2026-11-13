# Docker cluster

## Services

| Container | Hostname | Role |
|-----------|----------|------|
| spark-master | spark-master | Master UI + RPC |
| spark-worker-1 | spark-worker-1 | Executor |
| spark-worker-2 | spark-worker-2 | Executor |
| jupyter-lab | jupyter-lab | Jupyter + Spark driver (client mode) |

Host **port mappings** live in `docker-compose.yml`. Adjust them if defaults conflict on your machine.

## Commands

From repository root:

```bash
docker compose -f docker/docker-compose.yml up -d --build
docker compose -f docker/docker-compose.yml down
docker compose -f docker/docker-compose.yml logs -f
```

## Troubleshooting

### Worker cannot connect to master

```bash
docker logs spark-master
docker logs spark-worker-1
```

### Jupyter driver networking

Client-mode driver in `jupyter-lab` needs `spark.driver.host=jupyter-lab` and `spark.driver.bindAddress=0.0.0.0` (set in `spark-defaults.conf`).

### Permission errors on `data/output`

```bash
docker compose -f docker/docker-compose.yml down -v
docker compose -f docker/docker-compose.yml up -d --build
```

`entrypoint-init.sh` creates output dirs and fixes ownership on startup.

### Custom ports

If you remap Jupyter or the app UI, set `MASTER_UI_URL` / `APP_UI_URL` in `shared/config.py` (or pass env vars) so `ui_links()` in notebooks matches your browser URLs.
