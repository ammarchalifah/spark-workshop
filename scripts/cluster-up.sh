#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml up -d

echo ""
echo "Cluster starting."
echo "  Jupyter Lab:  http://localhost:8888"
echo "  Spark Master: http://localhost:8080"
echo "  Spark App UI: http://localhost:4040 (after running a notebook)"
echo ""
echo "Follow logs: ./scripts/cluster-logs.sh"
