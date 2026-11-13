#!/usr/bin/env python3
"""Generate workshop notebook files."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

METADATA = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {"name": "python", "version": "3.11.0"},
}


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "metadata": {},
        "source": text.splitlines(keepends=True),
        "outputs": [],
        "execution_count": None,
    }


def write_nb(path: Path, cells: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nb = {"cells": cells, "metadata": METADATA, "nbformat": 4, "nbformat_minor": 5}
    path.write_text(json.dumps(nb, indent=1))
    print(f"Wrote {path.relative_to(ROOT)}")


def module_01():
    write_nb(
        ROOT / "01-how-spark-works/01_how_spark_works.ipynb",
        [
            md(
                "# Module 01 — How Spark Works\n\n"
                "Focus: distributed execution, reading the Spark UI, and how configs change the physical plan.\n\n"
                "Open http://localhost:4040 before running any **action**."
            ),
            code(
                "import sys\nsys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '.')\n\n"
                "from shared.spark_session import begin_module, ui_links, explain_plan\n"
                "from shared import config\n\n"
                "spark = begin_module('module-01-how-spark-works')\nui_links()"
            ),
            md("## Load Data\n\n`begin_module()` already fetched missing TLC files into `data/cache/`. Read Parquet from disk — Spark cannot read HTTPS directly."),
            code(
                "trips = spark.read.parquet(*config.yellow_taxi_paths())\n"
                "print(f'Trips loaded — run an action to see row count')"
            ),
            code(
                "print(f'Trips: {trips.count():,} rows')\n"
                "# First action → first job appears in the UI"
            ),
            md(
                "## Spark UI: Jobs, Stages, Tasks\n\n"
                "| UI level | Meaning |\n"
                "|----------|--------|\n"
                "| **Job** | Created by an **action** (count, show, write) |\n"
                "| **Stage** | Pipeline of work separated by a **shuffle** (data moving across the cluster) |\n"
                "| **Task** | One unit of work on one partition, on one executor |\n\n"
                "Transformations alone do not create jobs — they only build the plan."
            ),
            md("## 1. Aggregation\n\nA `groupBy` collects rows across the cluster. Check **Jobs** and **Stages** tabs."),
            code(
                "vendor_counts = trips.groupBy('VendorID').count().orderBy('count', ascending=False)\n"
                "vendor_counts.show()\n"
                "# How many jobs? stages? tasks per stage?"
            ),
            code("explain_plan(vendor_counts)"),
            md(
                "## 2. Window Function\n\n"
                "Window functions need rows from the same group on the same machine. "
                "That data movement creates a new **stage boundary** in the UI — look for **Shuffle Read/Write** metrics."
            ),
            code(
                "from pyspark.sql import Window\n"
                "from pyspark.sql.functions import row_number, col\n\n"
                "w = Window.partitionBy('VendorID').orderBy(col('tpep_pickup_datetime').desc())\n"
                "ranked = trips.withColumn('rn', row_number().over(w)).filter('rn <= 3')\n"
                "ranked.select('VendorID', 'tpep_pickup_datetime', 'rn').show(10)"
            ),
            code("explain_plan(ranked)"),
            md(
                "## 3. Combining Two Datasets\n\n"
                "When Spark combines two datasets, data must be aligned across executors. "
                "Don't worry about *how* yet — just observe that new stages appear and shuffle bytes increase."
            ),
            code(
                "zones = spark.read.option('header', True).csv(config.zones_path())\n"
                "enriched = trips.join(\n"
                "    zones.withColumnRenamed('LocationID', 'PULocationID'),\n"
                "    on='PULocationID',\n"
                "    how='left',\n"
                ")\n"
                "enriched.select('PULocationID', 'Zone', 'Borough', 'total_amount').show(5)"
            ),
            code("explain_plan(enriched)"),
            md(
                "## 4. The Physical Plan Is Not Fixed\n\n"
                "The same logical query can produce different physical plans depending on **configuration**. "
                "Spark chooses at runtime — your code alone does not determine the plan."
            ),
            code(
                "# Config A: fewer shuffle partitions\n"
                "spark.conf.set('spark.sql.shuffle.partitions', '8')\n"
                "plan_a = trips.groupBy('PULocationID').count()\n"
                "plan_a.explain('formatted')"
            ),
            code(
                "# Config B: more shuffle partitions\n"
                "spark.conf.set('spark.sql.shuffle.partitions', '200')\n"
                "plan_b = trips.groupBy('PULocationID').count()\n"
                "plan_b.explain('formatted')\n"
                "# Compare partition counts in the plan"
            ),
            code(
                "# Run both and compare task counts in the Stages tab\n"
                "plan_a.count()\n"
                "plan_b.count()"
            ),
            code(
                "# Reset to default\n"
                "spark.conf.unset('spark.sql.shuffle.partitions')"
            ),
            md(
                "## 5. Live Discussion (Walk Through Together)\n\n"
                "Pick one query above and answer together:\n"
                "1. How many jobs did the action create?\n"
                "2. Which stage has shuffle read/write?\n"
                "3. How many tasks ran in each stage?\n"
                "4. What changed when we altered `spark.sql.shuffle.partitions`?"
            ),
            md(
                "## Key Takeaways\n\n"
                "1. Transformations are lazy; **actions** trigger jobs.\n"
                "2. **Stages** split at shuffle boundaries — data moving across the cluster is expensive.\n"
                "3. The physical plan depends on **configs and runtime conditions**, not just your code."
            ),
        ],
    )


def module_02():
    write_nb(
        ROOT / "02-lazy-execution/02_lazy_execution.ipynb",
        [
            md(
                "# Module 02 — Lazy Execution\n\n"
                "Transformations build a DAG; actions execute it. "
                "We'll use **expensive** pipelines so duplicated work is obvious in the UI and in wall-clock time."
            ),
            code(
                "import sys\nimport time\n"
                "sys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '.')\n"
                "from pyspark.sql import Window\n"
                "from pyspark.sql.functions import col, row_number, sum as _sum, avg, count\n"
                "from pyspark import StorageLevel\n"
                "from pyspark.sql import Observation\n"
                "from shared.spark_session import get_spark, ui_links\n"
                "from shared import config\n\n"
                "spark = get_spark('module-02-lazy-execution')\nui_links()"
            ),
            code("trips = spark.read.parquet(*config.yellow_taxi_paths())"),
            md("## Expensive Pipeline Helper\n\nFilter → window → aggregate → sort. Each action on this hurts."),
            code(
                "def expensive_pipeline(df):\n"
                "    w = Window.partitionBy('PULocationID').orderBy(col('total_amount').desc())\n"
                "    return (\n"
                "        df.filter('total_amount > 0 AND trip_distance > 0')\n"
                "        .withColumn('rn', row_number().over(w))\n"
                "        .filter('rn <= 100')\n"
                "        .groupBy('VendorID', 'PULocationID')\n"
                "        .agg(_sum('total_amount').alias('total'), avg('trip_distance').alias('avg_dist'))\n"
                "        .orderBy(col('total').desc())\n"
                "    )"
            ),
            md("## 1. Lazy Transformations\n\nBuild the pipeline — no jobs until an action."),
            code(
                "pipeline = expensive_pipeline(trips)\n"
                "print('Pipeline defined. Check Jobs tab — no new job yet.')"
            ),
            code(
                "t0 = time.perf_counter()\n"
                "n = pipeline.count()\n"
                "print(f'Rows: {n:,}  Time: {time.perf_counter() - t0:.1f}s')"
            ),
            md(
                "## 2. Branching DAG — Duplicated Work\n\n"
                "The same expensive ancestor is reused in **two actions**. "
                "Without caching, Spark re-runs the entire pipeline twice — watch duplicated stages in the UI."
            ),
            code(
                "base = expensive_pipeline(trips)\n\n"
                "t0 = time.perf_counter()\n"
                "a = base.count()\n"
                "t1 = time.perf_counter()\n"
                "b = base.filter('total > 100').count()\n"
                "t2 = time.perf_counter()\n\n"
                "print(f'Action 1 (count):       {a:,} rows  {t1 - t0:.1f}s')\n"
                "print(f'Action 2 (filter+count): {b:,} rows  {t2 - t1:.1f}s')\n"
                "print(f'Total: {t2 - t0:.1f}s  — compare to a single action above')"
            ),
            md(
                "## 3. Three Actions — Even Worse\n\n"
                "A third branch multiplies the pain. Note shuffle stages repeating in the UI."
            ),
            code(
                "base = expensive_pipeline(trips)\n\n"
                "t0 = time.perf_counter()\n"
                "r1 = base.count()\n"
                "r2 = base.filter('avg_dist > 2').count()\n"
                "r3 = base.groupBy('VendorID').count().count()\n"
                "print(f'Three actions total: {time.perf_counter() - t0:.1f}s')"
            ),
            md("## 4. Mitigation: Cache\n\nMaterialize once, reuse everywhere."),
            code(
                "base_cached = expensive_pipeline(trips).persist(StorageLevel.MEMORY_AND_DISK)\n\n"
                "t0 = time.perf_counter()\n"
                "base_cached.count()  # materializes\n"
                "t_mat = time.perf_counter()\n"
                "a = base_cached.count()\n"
                "b = base_cached.filter('total > 100').count()\n"
                "c = base_cached.groupBy('VendorID').count().count()\n"
                "t_end = time.perf_counter()\n\n"
                "print(f'Materialize: {t_mat - t0:.1f}s')\n"
                "print(f'3 cached actions: {t_end - t_mat:.1f}s')\n"
                "base_cached.unpersist()"
            ),
            md("## 5. Mitigation: Checkpoint\n\nBreaks lineage by writing intermediate results to storage."),
            code(
                "spark.sparkContext.setCheckpointDir(str(config.CHECKPOINT_DIR))\n\n"
                "cp = expensive_pipeline(trips).checkpoint()\n"
                "t0 = time.perf_counter()\n"
                "cp.count()\n"
                "print(f'Checkpoint materialize: {time.perf_counter() - t0:.1f}s')\n\n"
                "t0 = time.perf_counter()\n"
                "cp.count()\n"
                "cp.filter('total > 50').count()\n"
                "print(f'Post-checkpoint actions: {time.perf_counter() - t0:.1f}s')"
            ),
            md("## 6. Spark Observation — Metrics in a Single Action"),
            code(
                "obs = Observation('metrics')\n"
                "observed = expensive_pipeline(trips).observe(obs, count('*'))\n"
                "observed.count()\n"
                "print(obs.get)"
            ),
            md(
                "## 7. Live Discussion (Walk Through Together)\n\n"
                "1. How many shuffle stages repeated across the three uncached actions?\n"
                "2. How much time did caching save?\n"
                "3. When would you choose checkpoint over cache?"
            ),
            md(
                "## Key Takeaways\n\n"
                "1. Only **actions** trigger execution.\n"
                "2. Shared ancestors in branched DAGs cause **duplicate work** — expensive pipelines make this visible.\n"
                "3. Use `.cache()`, `.checkpoint()`, and `Observation` to control cost."
            ),
        ],
    )


def module_03():
    write_nb(
        ROOT / "03-storage-io/03_storage_io.ipynb",
        [
            md("# Module 03 — Storage I/O Performance\n\nCompare read/write performance across formats."),
            code(
                "import sys\nsys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '.')\n"
                "from shared.spark_session import get_spark\nfrom shared import config\nfrom shared.utils import timed_action, drop_iceberg_table\n\n"
                "spark = get_spark('module-03-storage-io')\n"
                "trips = spark.read.parquet(*config.yellow_taxi_paths())\n"
                "sample = trips.limit(500_000)"
            ),
            md("## Read Benchmarks"),
            code(
                "out = config.OUTPUT_BASE / '03-read-bench'\nout.mkdir(parents=True, exist_ok=True)\n\n"
                "drop_iceberg_table(spark, 'local.default.taxi_sample')\n\n"
                "sample.write.mode('overwrite').json(str(out / 'json'))\n"
                "sample.write.mode('overwrite').parquet(str(out / 'parquet'))\n"
                "sample.writeTo('local.default.taxi_sample').using('iceberg').create()"
            ),
            code(
                "results = {}\n\n"
                "_, t = timed_action(spark.read.json(str(out / 'json')))\nresults['json'] = t\n\n"
                "spark.conf.set('spark.sql.parquet.enableVectorizedReader', 'false')\n"
                "_, t = timed_action(spark.read.parquet(str(out / 'parquet')))\nresults['parquet_serial'] = t\n\n"
                "spark.conf.set('spark.sql.parquet.enableVectorizedReader', 'true')\n"
                "_, t = timed_action(spark.read.parquet(str(out / 'parquet')))\nresults['parquet_vectorized'] = t\n\n"
                "_, t = timed_action(spark.table('local.default.taxi_sample'))\nresults['iceberg'] = t\n\n"
                "for fmt, sec in sorted(results.items(), key=lambda x: x[1]):\n    print(f'{fmt:20s} {sec:.2f}s')"
            ),
            md("## Write Benchmarks"),
            code(
                "write_out = config.OUTPUT_BASE / '03-write-bench'\nwrite_out.mkdir(parents=True, exist_ok=True)\n"
                "drop_iceberg_table(spark, 'local.default.taxi_write_bench')\n\n"
                "write_results = {}\nimport time\n\n"
                "for fmt, writer in [\n"
                "    ('json', lambda: sample.write.mode('overwrite').json(str(write_out / 'json'))),\n"
                "    ('csv', lambda: sample.write.mode('overwrite').option('header', True).csv(str(write_out / 'csv'))),\n"
                "    ('parquet', lambda: sample.write.mode('overwrite').parquet(str(write_out / 'parquet'))),\n"
                "    ('iceberg', lambda: sample.writeTo('local.default.taxi_write_bench').using('iceberg').create()),\n"
                "]:\n"
                "    start = time.perf_counter()\n    writer()\n    write_results[fmt] = time.perf_counter() - start\n\n"
                "for fmt, sec in sorted(write_results.items(), key=lambda x: x[1]):\n    print(f'{fmt:10s} write: {sec:.2f}s')"
            ),
            md("## Key Takeaways\n\n1. Columnar formats outperform row-based.\n2. Vectorized Parquet reader is faster than serial.\n3. Iceberg adds metadata overhead on write but enables pruning on read."),
        ],
    )


def module_04():
    write_nb(
        ROOT / "04-udfs/04_udfs.ipynb",
        [
            md("# Module 04 — UDF Performance"),
            code(
                "import sys\nimport hashlib\nsys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '.')\n"
                "from pyspark.sql.functions import udf, pandas_udf, sha2, col\n"
                "from pyspark.sql.types import StringType\nimport pandas as pd\n"
                "from shared.spark_session import get_spark\nfrom shared import config\nfrom shared.utils import timed_action\n\n"
                "spark = get_spark('module-04-udfs')\n"
                "df = spark.read.parquet(*config.yellow_taxi_paths()).select('PULocationID').filter('PULocationID IS NOT NULL').limit(1_000_000)"
            ),
            md("## Python UDF"),
            code(
                "@udf(StringType())\ndef py_hash(val):\n    if val is None: return None\n    return hashlib.md5(str(val).encode()).hexdigest()\n\n"
                "result_py = df.withColumn('h', py_hash('PULocationID'))\n_, t_py = timed_action(result_py)\nprint(f'Python UDF: {t_py:.2f}s')"
            ),
            md("## Pandas UDF (Arrow)"),
            code(
                "@pandas_udf(StringType())\ndef pandas_hash(series: pd.Series) -> pd.Series:\n    return series.astype(str).apply(lambda x: hashlib.md5(x.encode()).hexdigest())\n\n"
                "result_pandas = df.withColumn('h', pandas_hash('PULocationID'))\n_, t_pandas = timed_action(result_pandas)\nprint(f'Pandas UDF: {t_pandas:.2f}s')"
            ),
            md("## Native Spark"),
            code(
                "result_native = df.withColumn('h', sha2(col('PULocationID').cast('string'), 256))\n"
                "_, t_native = timed_action(result_native)\nprint(f'Native Spark: {t_native:.2f}s')\n"
                "print(f'Speedup vs Python UDF — Pandas: {t_py/t_pandas:.1f}x, Native: {t_py/t_native:.1f}x')"
            ),
            md("## Key Takeaways\n\nPrefer native Spark → Pandas UDF → Python UDF."),
        ],
    )


def module_05():
    write_nb(
        ROOT / "05-shuffle-sort/05_shuffle_sort.ipynb",
        [
            md("# Module 05 — Shuffle & Sort"),
            code(
                "import sys\nsys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '.')\n"
                "from shared.spark_session import begin_module\nfrom shared import config\nfrom shared.utils import drop_iceberg_table\n\n"
                "spark = begin_module('module-05-shuffle-sort')\n"
                "trips = spark.read.parquet(*config.yellow_taxi_paths())\n"
                "zones = spark.read.option('header', True).csv(config.zones_path())"
            ),
            md("## Join Strategies"),
            code(
                "spark.conf.set('spark.sql.autoBroadcastJoinThreshold', '50MB')\n"
                "trips.join(zones.withColumnRenamed('LocationID', 'PULocationID'), 'PULocationID').explain('formatted')"
            ),
            code(
                "spark.conf.set('spark.sql.autoBroadcastJoinThreshold', '-1')\n"
                "trips.join(zones.withColumnRenamed('LocationID', 'PULocationID'), 'PULocationID').explain('formatted')"
            ),
            md("## Storage Partitioned Join (SPJ)"),
            code(
                "spark.conf.set('spark.sql.sources.v2.bucketing.enabled', 'true')\n"
                "spark.conf.set('spark.sql.sources.v2.bucketing.pushPartValues.enabled', 'true')\n"
                "spark.conf.set('spark.sql.iceberg.planning.preserve-data-grouping', 'true')\n"
                "spark.conf.set('spark.sql.requireAllClusterKeysForCoPartition', 'false')\n"
                "spark.conf.set('spark.sql.autoBroadcastJoinThreshold', '-1')"
            ),
            code(
                "trips_a = trips.select('VendorID', 'PULocationID', 'total_amount', 'tpep_pickup_datetime')\n"
                "trips_b = trips.select('VendorID', 'PULocationID', 'total_amount', 'tpep_dropoff_datetime')\n\n"
                "drop_iceberg_table(spark, 'local.default.trips_a')\n"
                "drop_iceberg_table(spark, 'local.default.trips_b')\n\n"
                "trips_a.writeTo('local.default.trips_a').using('iceberg').partitionedBy('PULocationID').create()\n"
                "trips_b.writeTo('local.default.trips_b').using('iceberg').partitionedBy('PULocationID').create()"
            ),
            code(
                "spj = spark.sql('''SELECT a.VendorID, a.total_amount, b.total_amount\n"
                "    FROM local.default.trips_a a JOIN local.default.trips_b b\n"
                "    ON a.PULocationID = b.PULocationID AND a.VendorID = b.VendorID''')\n"
                "spj.explain('formatted')\n"
                "# SPJ success: no Exchange before the join\n"
                "spj.limit(10).show()"
            ),
            md("### Compare: SPJ off → Exchange appears"),
            code(
                "spark.conf.set('spark.sql.sources.v2.bucketing.enabled', 'false')\n"
                "spark.conf.set('spark.sql.iceberg.planning.preserve-data-grouping', 'false')\n\n"
                "no_spj = spark.sql('''SELECT a.VendorID, a.total_amount, b.total_amount\n"
                "    FROM local.default.trips_a a JOIN local.default.trips_b b\n"
                "    ON a.PULocationID = b.PULocationID AND a.VendorID = b.VendorID''')\n"
                "no_spj.explain('formatted')\n\n"
                "spark.conf.set('spark.sql.sources.v2.bucketing.enabled', 'true')\n"
                "spark.conf.set('spark.sql.iceberg.planning.preserve-data-grouping', 'true')"
            ),
            md("## Table Ordering"),
            code(
                "drop_iceberg_table(spark, 'local.default.trips_ordered')\n"
                "spark.table('local.default.trips_a').writeTo('local.default.trips_ordered').using('iceberg').create()\n"
                "spark.sql('ALTER TABLE local.default.trips_ordered WRITE ORDERED BY (PULocationID, total_amount)')\n"
                "spark.sql(\"SHOW TBLPROPERTIES local.default.trips_ordered\").filter(\"key LIKE 'write.%' OR key = 'sort-order'\").show(truncate=False)"
            ),
            md("## Key Takeaways\n\n1. Broadcast avoids shuffle for small tables.\n2. SPJ eliminates shuffle when Iceberg partitions align.\n3. Table sort order improves reads but adds write cost."),
        ],
    )


def module_06():
    write_nb(
        ROOT / "06-java-gc/06_java_gc.ipynb",
        [
            md("# Module 06 — JVM and GC"),
            code(
                "import sys\nsys.path.insert(0, '/workspace')\n"
                "from shared.spark_session import begin_module, ui_links\nfrom shared import config\nfrom shared.utils import timed_action\n\n"
                "spark = begin_module('module-06-java-gc')\nui_links()"
            ),
            md("## Driver vs executor memory"),
            code(
                "for item in ['spark.driver.memory', 'spark.executor.memory', 'spark.memory.fraction']:\n"
                "    print(f'{item}: {spark.conf.get(item, \"default\")}')"
            ),
            md("## GC under load"),
            code(
                "trips = spark.read.parquet(*config.yellow_taxi_paths())\n"
                "heavy = trips.groupBy('PULocationID', 'DOLocationID', 'VendorID').count()\n"
                "_, t = timed_action(heavy)\nprint(f'Aggregation: {t:.2f}s — open Executors tab and inspect GC Time')"
            ),
            md("## Key Takeaways\n\n1. Read GC Time on the Executors tab before changing JVM flags.\n2. Driver OOM and executor OOM show up in different UI places and logs.\n3. `spark.memory.fraction` splits on-heap space between execution and storage."),
        ],
    )


if __name__ == "__main__":
    module_01()
    module_02()
    module_03()
    module_04()
    module_05()
    module_06()
    print("Done.")
