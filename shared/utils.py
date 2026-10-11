"""Workshop helper utilities."""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Generator

from pyspark.sql import DataFrame


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


def reset_spark_configs(spark, configs: dict[str, str | None]) -> None:
    """Set Spark configs, passing None to unset."""
    for key, value in configs.items():
        if value is None:
            spark.conf.unset(key)
        else:
            spark.conf.set(key, value)
