#!/usr/bin/env bash
# Pre-download NYC TLC datasets into data/cache/ (optional; notebooks can download at runtime).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
mkdir -p data/cache

BASE="https://d37ci6vzurychx.cloudfront.net"

echo "Downloading NYC TLC datasets into data/cache/ ..."

curl -fL -o data/cache/yellow_tripdata_2024-01.parquet \
  "${BASE}/trip-data/yellow_tripdata_2024-01.parquet"
curl -fL -o data/cache/yellow_tripdata_2024-02.parquet \
  "${BASE}/trip-data/yellow_tripdata_2024-02.parquet"
curl -fL -o data/cache/taxi_zone_lookup.csv \
  "${BASE}/misc/taxi_zone_lookup.csv"

echo "Done. Cached files are under data/cache/"
