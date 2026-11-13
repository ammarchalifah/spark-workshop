# Python requirements (Docker image)

`requirements.txt` is copied into `docker/Dockerfile` and installed with `pip` when you build the cluster image. It is **not** meant for a host virtual environment unless you are editing the repo with local IDE support.

- `pyspark` — matches the Spark version in the base image  
- `jupyterlab` — started by `entrypoint-jupyter.sh`  
- `pandas`, `pyarrow`, `ipykernel` — notebook and Pandas UDF module  

Change this file when you add notebook dependencies, then rebuild the image:

```bash
docker compose -f docker/docker-compose.yml up -d --build
```
