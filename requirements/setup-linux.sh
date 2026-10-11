#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== Spark Workshop Setup (Linux) ==="

# Check Java
if ! command -v java &>/dev/null; then
    echo "Java not found. Install with: sudo apt install openjdk-17-jdk"
    exit 1
fi
echo "Java: $(java -version 2>&1 | head -1)"

# Check Docker
if ! command -v docker &>/dev/null; then
    echo "Docker not found. Install with: sudo apt install docker.io docker-compose-v2"
    exit 1
fi
echo "Docker: $(docker --version)"

# Python venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements/requirements.txt

echo ""
echo "Setup complete!"
echo "  make cache-data   # optional: pre-download datasets"
echo "  make up           # start Docker cluster"
echo "  Open http://localhost:8888 in your browser"
