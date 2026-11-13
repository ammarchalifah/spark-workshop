#!/bin/bash
set -euo pipefail

command -v docker >/dev/null || {
    echo "Docker not found — install Docker Desktop: https://docs.docker.com/desktop/setup/install/mac-install/"
    exit 1
}

docker compose version >/dev/null || {
    echo "Docker Compose plugin not found — update Docker Desktop"
    exit 1
}

echo "docker: $(docker --version)"
echo "compose: $(docker compose version)"
