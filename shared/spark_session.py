"""Single Spark session entrypoint for all workshop notebooks."""

from __future__ import annotations

import atexit
import os
from typing import Any

from pyspark.sql import SparkSession

from shared import config

_spark: SparkSession | None = None
_cleanup_registered = False


def _stop_orphan_sessions() -> None:
    """Stop any SparkSession left over from a prior kernel or interrupted run."""
    active = SparkSession.getActiveSession()
    if active is not None:
        active.stop()


def stop_spark() -> None:
    """Stop the active SparkSession and release the UI port."""
    global _spark
    if _spark is not None:
        _spark.stop()
        _spark = None
    _stop_orphan_sessions()


def _register_cleanup() -> None:
    """Ensure Spark stops when the kernel process exits."""
    global _cleanup_registered
    if _cleanup_registered:
        return
    atexit.register(stop_spark)
    _cleanup_registered = True


def get_spark(app_name: str = "spark-workshop", extra_configs: dict[str, str] | None = None) -> SparkSession:
    """
    Create or return the workshop SparkSession.

    All notebooks should use this function instead of building SparkSession directly.
    """
    global _spark
    if _spark is not None:
        return _spark

    if not config.IN_DOCKER:
        raise RuntimeError(
            "Spark sessions run only inside the Docker Jupyter container. "
            "Start the cluster (see README), open http://localhost:8888, and run notebooks there."
        )

    config.ensure_output_dirs()
    _register_cleanup()

    builder = (
        SparkSession.builder.appName(app_name)
        .master(config.SPARK_MASTER)
        .config("spark.ui.port", "4040")
        .config("spark.ui.bindAddress", "0.0.0.0")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config(f"spark.sql.catalog.{config.CATALOG_NAME}", "org.apache.iceberg.spark.SparkCatalog")
        .config(f"spark.sql.catalog.{config.CATALOG_NAME}.type", "hadoop")
        .config(f"spark.sql.catalog.{config.CATALOG_NAME}.warehouse", str(config.WAREHOUSE_DIR))
        .config("spark.sql.defaultCatalog", config.CATALOG_NAME)
        .config("spark.eventLog.enabled", "true")
        .config("spark.eventLog.dir", str(config.OUTPUT_BASE / "spark-events"))
    )

    if config.IN_DOCKER:
        builder = builder.config("spark.driver.host", os.environ.get("SPARK_DRIVER_HOST", "jupyter-lab"))
        builder = builder.config("spark.driver.bindAddress", "0.0.0.0")

    if extra_configs:
        for key, value in extra_configs.items():
            builder = builder.config(key, value)

    _spark = builder.getOrCreate()
    _spark.sparkContext.setLogLevel("WARN")
    return _spark


def begin_module(app_name: str, extra_configs: dict[str, str] | None = None) -> SparkSession:
    """
    Start a clean Spark session for a new module notebook.

    Call this in the first cell of every module — especially after shutting down
    a previous kernel. Stops any leftover session and binds the UI to port 4040.
    """
    stop_spark()
    return get_spark(app_name, extra_configs=extra_configs)


def ui_links() -> dict[str, str]:
    """Return host-facing Spark UI URLs for notebook display."""
    links = {
        "master_ui": config.MASTER_UI_URL,
        "app_ui": config.APP_UI_URL,
        "worker_1_ui": "http://localhost:8081",
        "worker_2_ui": "http://localhost:8082",
    }
    if _spark is not None:
        links["app_ui_internal"] = _spark.sparkContext.uiWebUrl
    return links


def explain_plan(df: Any, mode: str = "formatted") -> None:
    """Print a DataFrame physical plan."""
    df.explain(mode)
