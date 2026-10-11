"""Single Spark session entrypoint for all workshop notebooks."""

from __future__ import annotations

import os
from typing import Any

from pyspark.sql import SparkSession

from shared import config

_spark: SparkSession | None = None


def get_spark(app_name: str = "spark-workshop", extra_configs: dict[str, str] | None = None) -> SparkSession:
    """
    Create or return the workshop SparkSession.

    All notebooks should use this function instead of building SparkSession directly.
    """
    global _spark
    if _spark is not None:
        return _spark

    config.ensure_output_dirs()

    builder = (
        SparkSession.builder.appName(app_name)
        .master(config.SPARK_MASTER)
        .config("spark.ui.port", "4040")
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


def stop_spark() -> None:
    """Stop the active SparkSession."""
    global _spark
    if _spark is not None:
        _spark.stop()
        _spark = None


def ui_links() -> dict[str, str]:
    """Return host-facing Spark UI URLs for notebook display."""
    return {
        "master_ui": config.MASTER_UI_URL,
        "app_ui": config.APP_UI_URL,
        "worker_1_ui": "http://localhost:8081",
        "worker_2_ui": "http://localhost:8082",
    }


def explain_plan(df: Any, mode: str = "formatted") -> None:
    """Print a DataFrame physical plan."""
    df.explain(mode)
