#!/bin/bash
# Preflight: Docker only (Java, Python, PySpark, Jupyter live in the cluster image).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== Spark lab preflight (Linux) ==="

if ! command -v docker &>/dev/null; then
    echo "Docker not found. Example install:"
    echo "  sudo apt install docker.io docker-compose-plugin"
    echo "  sudo usermod -aG docker \$USER   # then log out and back in"
    exit 1
fi

if ! docker compose version &>/dev/null; then
    echo "Docker Compose plugin not found. Install docker-compose-plugin."
    exit 1
fi

if ! docker info &>/dev/null; then
    echo "Docker daemon not reachable. Start the service or check group membership (docker group)."
    exit 1
fi

echo "Docker: $(docker --version)"
echo "Compose: $(docker compose version)"
echo ""
echo "Next steps:"
echo "  ./scripts/cache-data.sh   # optional: pre-download datasets"
echo "  ./scripts/cluster-up.sh   # build image and start cluster"
echo "  Open http://localhost:8888 in your browser"
