"""Central configuration for the Spark workshop."""

from __future__ import annotations

import os
import urllib.request
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


def _download(url: str, dest: Path) -> None:
    """Download a file if not already cached."""
    if dest.exists():
        return
    print(f"Downloading {dest.name} (~50 MB, first run only)...")
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)
    print(f"Cached at {dest}")


def ensure_workshop_data() -> None:
    """
    Download workshop datasets to data/cache/ if missing.

    Spark cannot read Parquet directly from HTTPS URLs — files must be local
    (or on a supported filesystem like S3/HDFS with proper config).
    """
    for year, month in WORKSHOP_MONTHS:
        name = f"yellow_tripdata_{year}-{month:02d}.parquet"
        _download(yellow_taxi_url(year, month), CACHE_DIR / name)

    _download(TLC_ZONES, CACHE_DIR / "taxi_zone_lookup.csv")


def yellow_taxi_paths() -> list[str]:
    """Return local paths to cached yellow taxi Parquet files."""
    ensure_workshop_data()
    return [str(CACHE_DIR / f"yellow_tripdata_{year}-{month:02d}.parquet") for year, month in WORKSHOP_MONTHS]


def zones_path() -> str:
    """Return local path to cached taxi zone lookup CSV."""
    ensure_workshop_data()
    return str(CACHE_DIR / "taxi_zone_lookup.csv")


def ensure_output_dirs() -> None:
    """Create output directories if they do not exist."""
    for d in [OUTPUT_BASE, WAREHOUSE_DIR, CHECKPOINT_DIR, CACHE_DIR]:
        d.mkdir(parents=True, exist_ok=True)
