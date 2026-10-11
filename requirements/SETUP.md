# Cross-Platform Setup Guide

This workshop supports **macOS**, **Linux**, and **Windows**. The recommended path is Docker; local mode is available as a fallback.

## Requirements

| Component | Version | Notes |
|-----------|---------|-------|
| Java | 17 or 21 | Required for PySpark (local mode) and matches Docker image |
| Python | 3.10+ | 3.11 recommended |
| Docker | Latest | Docker Desktop (macOS/Windows) or Docker Engine (Linux) |
| RAM | 8 GB+ | 16 GB recommended for comfortable multi-node cluster |

## Quick Setup Scripts

```bash
# macOS
./requirements/setup-macos.sh

# Linux
./requirements/setup-linux.sh

# Windows (PowerShell)
.\requirements\setup-windows.ps1
```

## macOS

### Java 17

```bash
brew install openjdk@17
echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc
echo 'export JAVA_HOME="/opt/homebrew/opt/openjdk@17"' >> ~/.zshrc
source ~/.zshrc
java -version
```

Intel Macs: replace `/opt/homebrew` with `/usr/local`.

### Python

```bash
brew install python@3.11
python3 --version
```

### Docker

Install [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/).

## Linux (Ubuntu/Debian)

### Java 17

```bash
sudo apt update
sudo apt install -y openjdk-17-jdk
java -version
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

### Python

```bash
sudo apt install -y python3.11 python3.11-venv python3-pip
python3 --version
```

### Docker

```bash
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
# Log out and back in for group membership
```

## Windows

### Java 17

```powershell
winget install EclipseAdoptium.Temurin.17.JDK
java -version
```

Set `JAVA_HOME` to the Temurin install path (e.g. `C:\Program Files\Eclipse Adoptium\jdk-17*`).

### Python

Download Python 3.11 from [python.org](https://www.python.org/downloads/) and check "Add to PATH".

### Docker

Install [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) with WSL2 backend enabled.

## Python Virtual Environment

After installing prerequisites:

```bash
cd spark-workshop
make setup
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\Activate.ps1  # Windows
```

## Verify Installation

```bash
java -version          # Should show 17 or 21
python3 --version      # Should show 3.10+
docker --version
make up                # Start cluster
```

Open http://localhost:8888 for Jupyter Lab.

## Local Mode (No Docker)

If Docker is unavailable:

```bash
source .venv/bin/activate
export SPARK_MASTER='local[*]'
export JAVA_HOME=<path-to-java-17>
jupyter lab
```

Notebooks will run Spark in local mode. Outputs go to `./data/output/`.

## Iceberg JAR (Local Mode Only)

In Docker, the Iceberg JAR is pre-installed. For local mode, download:

```bash
mkdir -p jars
curl -fL -o jars/iceberg-spark-runtime-4.1_2.13-1.12.0.jar \
  "https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-4.1_2.13/1.12.0/iceberg-spark-runtime-4.1_2.13-1.12.0.jar"
```

Then set in your notebook or environment:

```python
.config("spark.jars", "jars/iceberg-spark-runtime-4.1_2.13-1.12.0.jar")
```
