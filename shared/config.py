"""Central configuration for the Spark workshop."""

from __future__ import annotations

import os
from pathlib import Path

# Detect Docker vs local mode
IN_DOCKER = Path("/workspace").exists() and os.environ.get("SPARK_DRIVER_HOST") == "jupyter-lab"
WORKSPACE_ROOT = Path("/workspace") if IN_DOCKER else Path(__file__).resolve().parent.parent

# Paths
DATA_ROOT = WORKSPACE_ROOT / "data"
CACHE_DIR = DATA_ROOT / "cache"
OUTPUT_BASE = DATA_ROOT / "output"
WAREHOUSE_DIR = OUTPUT_BASE / "warehouse"
CHECKPOINT_DIR = OUTPUT_BASE / "checkpoints"

# Spark cluster
SPARK_MASTER = os.environ.get("SPARK_MASTER", "spark://spark-master:7077" if IN_DOCKER else "local[*]")
CATALOG_NAME = "local"

# Public data URLs (NYC TLC)
TLC_BASE = "https://d37ci6vzurychx.cloudfront.net"
TLC_YELLOW = f"{TLC_BASE}/trip-data/yellow_tripdata_{{year}}-{{month:02d}}.parquet"
TLC_ZONES = f"{TLC_BASE}/misc/taxi_zone_lookup.csv"

WORKSHOP_MONTHS: list[tuple[str, int]] = [("2024", 1), ("2024", 2)]

# UI URLs (host-facing)
MASTER_UI_URL = "http://localhost:8080"
APP_UI_URL = "http://localhost:4040"


def yellow_taxi_url(year: str, month: int) -> str:
    return TLC_YELLOW.format(year=year, month=month)


def yellow_taxi_paths() -> list[str]:
    """Return cached local paths if available, otherwise remote URLs."""
    paths: list[str] = []
    for year, month in WORKSHOP_MONTHS:
        cached = CACHE_DIR / f"yellow_tripdata_{year}-{month:02d}.parquet"
        if cached.exists():
            paths.append(str(cached))
        else:
            paths.append(yellow_taxi_url(year, month))
    return paths


def zones_path() -> str:
    cached = CACHE_DIR / "taxi_zone_lookup.csv"
    if cached.exists():
        return str(cached)
    return TLC_ZONES


def ensure_output_dirs() -> None:
    """Create output directories if they do not exist."""
    for d in [OUTPUT_BASE, WAREHOUSE_DIR, CHECKPOINT_DIR]:
        d.mkdir(parents=True, exist_ok=True)
