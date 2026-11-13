# Install Docker

The host machine needs **Docker** with the **Compose** plugin. Java, Python, PySpark, Jupyter, and the Iceberg JAR are installed **inside the cluster image** when you run `cluster-up` (see `docker/Dockerfile`).

Allocate **8 GB RAM or more** to Docker (16 GB is more comfortable).

## Preflight scripts

From the repository root:

```bash
chmod +x requirements/setup-macos.sh requirements/setup-linux.sh
./requirements/setup-macos.sh    # or setup-linux.sh
```

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\requirements\setup-windows.ps1
```

These scripts only verify Docker/Compose — they do not install Java or Python on the host.

## macOS

Install [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/).

- Settings → Resources: raise memory if the cluster OOMs.
- First cluster start runs `docker compose build` and pulls the Spark base image (several GB).

## Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
```

Log out and back in so `docker` runs without `sudo`.

```bash
sudo systemctl enable --now docker
docker compose version
```

## Windows

Install [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) with **WSL2** enabled.

Use PowerShell for `cluster-up.ps1`, or Git Bash for `cluster-up.sh`.

## Start the lab

```bash
./scripts/cluster-up.sh
```

```powershell
.\scripts\cluster-up.ps1
```

Open http://localhost:8888.

## What runs where

| Component | Location |
|-----------|----------|
| Docker Engine / Desktop | Host |
| Java 17, Spark, PySpark | Container image |
| Jupyter Lab kernel | `jupyter-lab` container |
| `requirements/requirements.txt` | Installed in image at **build** time |
| Notebooks, `shared/` | Bind-mounted from repo into `/workspace` |
| `data/cache`, `data/output` | Bind-mounted `./data` |

## Optional: host Python (contributors only)

You do **not** need a host venv to run the lab. If you edit notebooks outside Docker and want IDE type hints:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements/requirements.txt
```

Local `pip install pyspark` still does **not** replace the cluster — notebooks must run in Jupyter inside Docker.
