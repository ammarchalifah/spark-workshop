# Install Docker

You need **Docker** and the **Compose** plugin. The first `docker compose up --build` builds the Spark + Jupyter image (`docker/Dockerfile`). Give Docker **8 GB+ RAM** (16 GB recommended).

## Quick check (optional)

```bash
chmod +x requirements/setup-macos.sh requirements/setup-linux.sh
./requirements/setup-macos.sh    # macOS
# ./requirements/setup-linux.sh  # Linux or WSL
```

## macOS

[Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/)

## Linux

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
```

Log out and back in, then `docker compose version`.

## Windows

Use **Docker Desktop** with the **WSL2** backend. Clone the repo and run all commands from a **WSL** shell (Ubuntu recommended), not PowerShell:

```bash
cd /path/to/spark-workshop
docker compose -f docker/docker-compose.yml up -d --build
```

Keep the repo on the Linux filesystem (`~/...`), not `/mnt/c/...`, for reasonable bind-mount performance.

## Start / stop

From repo root:

```bash
docker compose -f docker/docker-compose.yml up -d --build
docker compose -f docker/docker-compose.yml down
docker compose -f docker/docker-compose.yml logs -f
```

Jupyter is on the host port mapped to `8888` in `docker/docker-compose.yml` (default http://localhost:8888).

## What runs where

| Component | Location |
|-----------|----------|
| Docker Engine | Host (or Docker Desktop VM) |
| Java, Spark, PySpark, Jupyter | Container image |
| `requirements/requirements.txt` | `pip install` at image build |
| Notebooks, `shared/` | Bind mount `..` → `/workspace` |
| `data/cache`, `data/output` | Bind mount `./data` |

You do not need Python or Java on the host to run the notebooks—use Jupyter inside Docker only.
