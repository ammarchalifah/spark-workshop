#!/usr/bin/env bash
# Stop cluster and remove cached/output data on the host bind mount.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

docker compose -f docker/docker-compose.yml down -v
rm -rf data/output data/cache

echo "Cluster stopped; data/output and data/cache cleared."
