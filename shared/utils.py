"""Workshop helper utilities."""

from __future__ import annotations

import shutil
import time
from contextlib import contextmanager
from typing import Generator

from pyspark.sql import DataFrame, SparkSession

from shared import config


@contextmanager
def timer(label: str = "operation") -> Generator[None, None, None]:
    """Context manager that prints elapsed wall-clock time."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"[{label}] completed in {elapsed:.2f}s")


def timed_action(df: DataFrame, action: str = "count") -> tuple[int | None, float]:
    """
    Run a DataFrame action and return (result, elapsed_seconds).

    Supported actions: count, collect (returns len).
    """
    start = time.perf_counter()
    if action == "count":
        result: int | None = df.count()
    elif action == "collect":
        result = len(df.collect())
    else:
        raise ValueError(f"Unsupported action: {action}")
    elapsed = time.perf_counter() - start
    return result, elapsed


def drop_iceberg_table(spark: SparkSession, table: str) -> None:
    """
    Drop an Iceberg table and remove leftover files.

    Use before create() when re-running workshop cells — createOrReplace() can
    fail on corrupted metadata from interrupted prior runs.
    """
    try:
        spark.sql(f"DROP TABLE IF EXISTS {table}")
    except Exception:
        pass

    # table format: catalog.db.name (e.g. local.default.taxi_sample)
    parts = table.split(".")
    if len(parts) >= 2:
        table_path = config.WAREHOUSE_DIR.joinpath(*parts[-2:])
        if table_path.exists():
            shutil.rmtree(table_path)


def reset_spark_configs(spark, configs: dict[str, str | None]) -> None:
    """Set Spark configs, passing None to unset."""
    for key, value in configs.items():
        if value is None:
            spark.conf.unset(key)
        else:
            spark.conf.set(key, value)
