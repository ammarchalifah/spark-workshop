# Python dependencies (cluster image)

These packages are installed in the **Docker image** when you build the stack (`docker/Dockerfile` reads this file).

| Package | Role |
|---------|------|
| `pyspark` | Spark version aligned with the base image |
| `jupyterlab` | Notebook server in `jupyter-lab` |
| `pandas`, `pyarrow` | Pandas UDF module |
| `ipykernel` | Jupyter kernels |

After changing `requirements.txt`, rebuild and restart:

```bash
docker compose -f docker/docker-compose.yml up -d --build
```