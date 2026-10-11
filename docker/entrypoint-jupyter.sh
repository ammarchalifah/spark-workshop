#!/bin/bash
set -euo pipefail

export HOME=/home/spark
export JUPYTER_RUNTIME_DIR=/workspace/data/.jupyter/runtime
export JUPYTER_DATA_DIR=/workspace/data/.jupyter/data
export JUPYTER_CONFIG_DIR=/workspace/data/.jupyter/config

cd /workspace

exec jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --ServerApp.token='' \
    --ServerApp.password='' \
    --ServerApp.root_dir=/workspace
