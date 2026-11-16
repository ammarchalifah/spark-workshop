"""Small synthetic datasets for teaching shuffle / join shape (module 05)."""

from __future__ import annotations

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F


def user_post_activity(spark: SparkSession, users: int = 50, posts_per_user: int = 40) -> tuple[DataFrame, DataFrame]:
    """
  `users` dimension and `events` fact — join on user_id; downstream agg keys matter for shuffle count.
  """
    user_df = spark.range(0, users).select(F.col("id").alias("user_id"))

    events = (
        spark.range(0, users * posts_per_user)
        .select(
            (F.col("id") % users).alias("user_id"),
            (F.col("id") % posts_per_user).alias("post_id"),
            F.col("id").alias("event_id"),
            (F.rand() * 100).alias("score"),
        )
    )
    return user_df, events