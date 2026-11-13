#!/bin/bash
# Preflight: Docker only (Java, Python, PySpark, Jupyter live in the cluster image).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== Spark lab preflight (macOS) ==="

if ! command -v docker &>/dev/null; then
    echo "Docker not found. Install Docker Desktop:"
    echo "  https://docs.docker.com/desktop/setup/install/mac-install/"
    exit 1
fi

if ! docker compose version &>/dev/null; then
    echo "Docker Compose plugin not found. Update Docker Desktop."
    exit 1
fi

echo "Docker: $(docker --version)"
echo "Compose: $(docker compose version)"
echo ""
echo "Next steps:"
echo "  ./scripts/cache-data.sh   # optional: pre-download datasets"
echo "  ./scripts/cluster-up.sh   # build image and start cluster"
echo "  open http://localhost:8888"
