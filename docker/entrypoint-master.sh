#!/bin/bash
set -euo pipefail

/opt/spark/sbin/start-master.sh -p 7077 --webui-port 8080

echo "Spark Master UI: http://localhost:8080"
tail -f /dev/null
