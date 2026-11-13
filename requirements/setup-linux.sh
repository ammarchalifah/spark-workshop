#!/bin/bash
set -euo pipefail

command -v docker >/dev/null || {
    echo "Docker not found — see requirements/SETUP.md"
    exit 1
}

docker compose version >/dev/null || {
    echo "Docker Compose plugin not found — see requirements/SETUP.md"
    exit 1
}

docker info >/dev/null || {
    echo "Cannot talk to Docker daemon (start dockerd or add user to docker group)"
    exit 1
}

echo "docker: $(docker --version)"
echo "compose: $(docker compose version)"
