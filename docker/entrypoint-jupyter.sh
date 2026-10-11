#!/bin/bash
set -euo pipefail

mkdir -p /workspace/data/output/warehouse /workspace/data/output/spark-events /workspace/data/cache

cd /workspace

exec jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root \
    --NotebookApp.token='' \
    --NotebookApp.password='' \
    --ServerApp.root_dir=/workspace
