#!/bin/bash
set -euo pipefail

mkdir -p /workspace/data/output/warehouse /workspace/data/output/spark-events

/opt/spark/sbin/start-master.sh -p 7077 --webui-port 8080

echo "Spark Master UI: http://localhost:8080"
tail -f /dev/null
