#!/bin/bash
# Fix volume permissions then drop to the Spark user.
set -euo pipefail

SPARK_UID="${SPARK_UID:-185}"
SPARK_GID="${SPARK_GID:-185}"

mkdir -p /home/spark \
         /workspace/data/output/warehouse \
         /workspace/data/output/spark-events \
         /workspace/data/cache \
         /workspace/data/.jupyter/runtime \
         /workspace/data/.jupyter/data \
         /workspace/data/.jupyter/config

chown -R "${SPARK_UID}:${SPARK_GID}" /workspace/data /home/spark

if [ "$(id -u)" = "0" ]; then
  exec gosu "${SPARK_UID}" env HOME=/home/spark "$@"
else
  exec env HOME=/home/spark "$@"
fi
