#!/bin/bash
set -euo pipefail

WEBUI_PORT="${SPARK_WORKER_WEBUI_PORT:-8081}"

/opt/spark/sbin/start-worker.sh spark://spark-master:7077 --webui-port "${WEBUI_PORT}"

echo "Spark Worker UI: http://localhost:${WEBUI_PORT}"
tail -f /dev/null
