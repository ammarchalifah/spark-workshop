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


def module_01_template():
    write_nb(
        ROOT / "01-how-spark-works/01_how_spark_works_template.ipynb",
        [
            md("# Module 01 — How Spark Works\n\nInstructor template. Open Spark UI before running actions."),
            code(
                "import sys\nsys.path.insert(0, '/workspace' if '/workspace' in sys.path[0] or __import__('pathlib').Path('/workspace').exists() else '.')\n\nfrom shared.spark_session import get_spark, ui_links, explain_plan\nfrom shared import config\n\nspark = get_spark('module-01-how-spark-works')\nui_links()"
            ),
            md("## Load Data\n\nNYC yellow taxi trips + zone lookup (public TLC dataset)."),
            code(
                "trips = spark.read.parquet(*config.yellow_taxi_paths())\nzones = spark.read.option('header', True).csv(config.zones_path())\nprint(f'Trips: {trips.count():,} rows')\nprint(f'Zones: {zones.count():,} rows')"
            ),
            md("## 1. Aggregation\n\nRun a `groupBy` + `count`. Open **Jobs** and **Stages** tabs at http://localhost:4040"),
            code(
                "vendor_counts = trips.groupBy('VendorID').count().orderBy('count', ascending=False)\nvendor_counts.show()\n# Observe: 1 job, typically 2 stages (partial agg + final agg or shuffle)"
            ),
            code("explain_plan(vendor_counts)"),
            md("## 2. Window Function\n\nWindow functions often trigger a shuffle to distribute rows within each partition group."),
            code(
                "from pyspark.sql import Window\nfrom pyspark.sql.functions import row_number, col\n\nw = Window.partitionBy('VendorID').orderBy(col('tpep_pickup_datetime').desc())\nranked = trips.withColumn('rn', row_number().over(w)).filter('rn <= 3')\nranked.select('VendorID', 'tpep_pickup_datetime', 'rn').show(10)\n# Observe: Exchange (shuffle) stage in UI"
            ),
            code("explain_plan(ranked)"),
            md("## 3. Join\n\nJoin trips to zone lookup on `PULocationID = LocationID`. Watch shuffle read/write in Stages tab."),
            code(
                "joined = trips.join(\n    zones.withColumnRenamed('LocationID', 'PULocationID'),\n    on='PULocationID',\n    how='left'\n)\njoined.select('PULocationID', 'Zone', 'Borough', 'total_amount').show(5)\n# Observe: BroadcastExchange (small zones table) or SortMergeJoin + Exchange"
            ),
            code("explain_plan(joined)"),
            md("## 4. Spark UI Literacy\n\n| UI Level | What it represents |\n|----------|--------------------|\n| **Job** | One action triggered this job |\n| **Stage** | Pipeline between shuffles |\n| **Task** | One partition's work on one executor |\n\nCheck **SQL** tab for the physical plan linked to each query."),
            md("## 5. Query Planner Non-Determinism\n\nThe same logical query can produce different physical plans depending on stats and configs."),
            code(
                "# Plan A: default broadcast threshold\nspark.conf.set('spark.sql.autoBroadcastJoinThreshold', '10MB')\nsmall = zones.limit(100)\nplan_a = trips.join(small.withColumnRenamed('LocationID', 'PULocationID'), 'PULocationID')\nplan_a.explain('formatted')"
            ),
            code(
                "# Plan B: disable broadcast — forces shuffle join\nspark.conf.set('spark.sql.autoBroadcastJoinThreshold', '-1')\nplan_b = trips.join(zones.withColumnRenamed('LocationID', 'PULocationID'), 'PULocationID')\nplan_b.explain('formatted')\n# Compare: BroadcastHashJoin vs SortMergeJoin"
            ),
            code(
                "# Reset\nspark.conf.set('spark.sql.autoBroadcastJoinThreshold', '10MB')"
            ),
            md("## Key Takeaways\n\n1. Transformations are lazy; actions trigger jobs.\n2. Shuffles (Exchange) create new stages — expensive in distributed systems.\n3. Catalyst chooses plans based on data size, stats, and configs — not fixed by your code alone."),
        ],
    )


def module_01_exercise():
    write_nb(
        ROOT / "01-how-spark-works/exercises/01_exercise.ipynb",
        [
            md("# Module 01 — Exercise\n\nIdentify jobs, stages, and plan changes in the Spark UI."),
            code(
                "import sys\nsys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '../..')\nfrom shared.spark_session import get_spark, ui_links\nfrom shared import config\n\nspark = get_spark('module-01-exercise')\nprint(ui_links())"
            ),
            code("trips = spark.read.parquet(*config.yellow_taxi_paths())\nzones = spark.read.option('header', True).csv(config.zones_path())"),
            md("## Task 1\n\nRun the aggregation below. In the Spark UI (http://localhost:4040):\n- How many **jobs** were created?\n- How many **stages**?\n- How many **tasks** in each stage?"),
            code(
                "# YOUR CODE: group by Borough (via join) and count trips\n# Hint: join trips to zones first\n\n# TODO: write join + groupBy + count + show\n"
            ),
            md("## Task 2\n\nRun a window function ranking trips by fare within each pickup zone. Identify the shuffle stage."),
            code(
                "# TODO: use Window.partitionBy('PULocationID').orderBy(col('total_amount').desc())\n# Show top 3 fares per zone\n"
            ),
            md("## Task 3\n\nDisable broadcast join and re-run the join. Compare physical plans."),
            code(
                "spark.conf.set('spark.sql.autoBroadcastJoinThreshold', '-1')\n# TODO: join and explain('formatted')\n"
            ),
        ],
    )


def module_02_template():
    write_nb(
        ROOT / "02-lazy-execution/02_lazy_execution_template.ipynb",
        [
            md("# Module 02 — Lazy Execution\n\nTransformations build a DAG; actions execute it."),
            code(
                "import sys\nsys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '.')\nfrom shared.spark_session import get_spark, ui_links\nfrom shared import config\n\nspark = get_spark('module-02-lazy-execution')\nui_links()"
            ),
            code("trips = spark.read.parquet(*config.yellow_taxi_paths())"),
            md("## 1. Lazy Transformations\n\nBuild a chain — no jobs until an action."),
            code(
                "from pyspark.sql.functions import col\n\ndf = (trips\n    .filter('total_amount > 0')\n    .select('VendorID', 'PULocationID', 'total_amount', 'trip_distance', 'tpep_pickup_datetime')\n    .filter('PULocationID IS NOT NULL')\n    .withColumn('fare_per_mile', col('total_amount') / col('trip_distance'))\n)\nprint('No jobs yet — check UI Jobs tab (should be empty or unchanged)')"
            ),
            code(
                "count = df.count()  # ACTION — triggers entire DAG\nprint(f'Row count: {count:,}')"
            ),
            md("## 2. Branching DAG — Duplicated Work\n\nReusing `df_filtered` in two actions scans the source twice."),
            code(
                "df_filtered = trips.filter('total_amount > 20')\n\nc1 = df_filtered.count()   # Action 1 — full scan\nc2 = df_filtered.filter('trip_distance > 5').count()  # Action 2 — scans df_filtered again\nprint(f'High fare trips: {c1:,}, long high-fare: {c2:,}')\n# UI: two jobs, duplicated scan stages"
            ),
            md("## 3. Wasteful Patterns\n\n`count()` + `filter().count()` on same base = repeated work."),
            code(
                "base = trips.filter('passenger_count > 0')\nn1 = base.count()\nn2 = base.filter('total_amount > 50').count()\nprint(f'Passengers>0: {n1:,}, Fare>50: {n2:,}')\n# Both actions re-read and re-filter from source"
            ),
            md("## 4. Mitigation: Cache"),
            code(
                "from pyspark import StorageLevel\n\nbase_cached = trips.filter('passenger_count > 0').persist(StorageLevel.MEMORY_AND_DISK)\nbase_cached.count()  # materializes cache\n\nn1 = base_cached.count()  # fast — from cache\nn2 = base_cached.filter('total_amount > 50').count()  # reads from cache\nprint(f'Cached: {n1:,}, Filtered: {n2:,}')\nbase_cached.unpersist()"
            ),
            md("## 5. Mitigation: Checkpoint\n\nBreaks lineage by writing to reliable storage."),
            code(
                "spark.sparkContext.setCheckpointDir(str(config.CHECKPOINT_DIR))\n\ncp = trips.filter('total_amount > 0').checkpoint()\ncp.count()  # writes checkpoint, then counts\n# Subsequent actions read from checkpoint, not full lineage"
            ),
            md("## 6. Spark Observation — Metrics Without Full Actions"),
            code(
                "from pyspark.sql import Observation\n\nobs = Observation('metrics')\nobserved = trips.filter('total_amount > 0').observe(obs, count('*'))\nobserved.count()  # single action collects observed metrics\nprint(obs.get)"
            ),
            md("## Key Takeaways\n\n1. Only **actions** trigger execution.\n2. Shared ancestors in branched DAGs cause **duplicate work** unless cached/checkpointed.\n3. Use `.cache()`, `.checkpoint()`, and `Observation` strategically."),
        ],
    )


def module_02_exercise():
    write_nb(
        ROOT / "02-lazy-execution/exercises/02_exercise.ipynb",
        [
            md("# Module 02 — Exercise\n\nFix duplicated work in a branched pipeline."),
            code(
                "import sys\nsys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '../..')\nfrom shared.spark_session import get_spark\nfrom shared import config\n\nspark = get_spark('module-02-exercise')\ntrips = spark.read.parquet(*config.yellow_taxi_paths())"
            ),
            md("## Task\n\nThis pipeline runs three actions on a shared base. Identify duplicated stages in the UI, then fix with the cheapest mitigation."),
            code(
                "base = trips.filter('trip_distance > 1')\n\n# Three actions — duplicated scans\na = base.count()\nb = base.filter('total_amount > 30').count()\nc = base.groupBy('VendorID').count().count()\nprint(a, b, c)"
            ),
            code(
                "# TODO: refactor using .cache() or .checkpoint() to avoid duplicate scans\n# Re-run and compare job/stage counts in Spark UI\n"
            ),
        ],
    )


def module_03_template():
    write_nb(
        ROOT / "03-storage-io/03_storage_io_template.ipynb",
        [
            md("# Module 03 — Storage I/O Performance\n\nCompare read/write performance across formats."),
            code(
                "import sys\nsys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '.')\nfrom shared.spark_session import get_spark\nfrom shared import config\nfrom shared.utils import timed_action\n\nspark = get_spark('module-03-storage-io')\ntrips = spark.read.parquet(*config.yellow_taxi_paths())\nsample = trips.limit(500_000)"
            ),
            md("## Read Benchmarks"),
            code(
                "out = config.OUTPUT_BASE / '03-read-bench'\nout.mkdir(parents=True, exist_ok=True)\n\n# Write sample in multiple formats for fair read comparison\nsample.write.mode('overwrite').json(str(out / 'json'))\nsample.write.mode('overwrite').parquet(str(out / 'parquet'))\nsample.writeTo('local.default.taxi_sample').using('iceberg').createOrReplace()"
            ),
            code(
                "results = {}\n\n# JSON read\n_, t = timed_action(spark.read.json(str(out / 'json')))\nresults['json'] = t\n\n# Parquet serial\nspark.conf.set('spark.sql.parquet.enableVectorizedReader', 'false')\n_, t = timed_action(spark.read.parquet(str(out / 'parquet')))\nresults['parquet_serial'] = t\n\n# Parquet vectorized\nspark.conf.set('spark.sql.parquet.enableVectorizedReader', 'true')\n_, t = timed_action(spark.read.parquet(str(out / 'parquet')))\nresults['parquet_vectorized'] = t\n\n# Iceberg\n_, t = timed_action(spark.table('local.default.taxi_sample'))\nresults['iceberg'] = t\n\nfor fmt, sec in sorted(results.items(), key=lambda x: x[1]):\n    print(f'{fmt:20s} {sec:.2f}s')"
            ),
            md("## Iceberg Filter Pushdown\n\nCompare files scanned with and without a filter."),
            code(
                "spark.table('local.default.taxi_sample').filter('total_amount > 100').explain('formatted')\n# Iceberg skips files using column stats in metadata"
            ),
            md("## Write Benchmarks"),
            code(
                "write_out = config.OUTPUT_BASE / '03-write-bench'\nwrite_out.mkdir(parents=True, exist_ok=True)\n\nwrite_results = {}\n\nfor fmt, writer in [\n    ('json', lambda: sample.write.mode('overwrite').json(str(write_out / 'json'))),\n    ('csv', lambda: sample.write.mode('overwrite').option('header', True).csv(str(write_out / 'csv'))),\n    ('parquet', lambda: sample.write.mode('overwrite').parquet(str(write_out / 'parquet'))),\n    ('iceberg', lambda: sample.writeTo('local.default.taxi_write_bench').using('iceberg').createOrReplace()),\n]:\n    spark.catalog.clearCache()\n    import time\n    start = time.perf_counter()\n    writer()\n    write_results[fmt] = time.perf_counter() - start\n\nfor fmt, sec in sorted(write_results.items(), key=lambda x: x[1]):\n    print(f'{fmt:10s} write: {sec:.2f}s')"
            ),
            md("## Key Takeaways\n\n1. Columnar formats (Parquet, Iceberg) outperform row-based (JSON, CSV).\n2. Vectorized Parquet reader is significantly faster than serial.\n3. Iceberg adds metadata overhead on write but enables pruning and ACID on read."),
        ],
    )


def module_03_exercise():
    write_nb(
        ROOT / "03-storage-io/exercises/03_exercise.ipynb",
        [
            md("# Module 03 — Exercise\n\nBenchmark read performance with filter pushdown."),
            code(
                "import sys\nsys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '../..')\nfrom shared.spark_session import get_spark\nfrom shared import config\nfrom shared.utils import timed_action\n\nspark = get_spark('module-03-exercise')\ntrips = spark.read.parquet(*config.yellow_taxi_paths())"
            ),
            md("## Task\n\nWrite 200k rows to both Parquet and Iceberg. Time reads with and without a filter on `total_amount > 50`."),
            code(
                "sample = trips.limit(200_000)\n# TODO: write to parquet and iceberg tables\n# TODO: time 4 reads (parquet filtered/unfiltered, iceberg filtered/unfiltered)\n"
            ),
        ],
    )


def module_04_template():
    write_nb(
        ROOT / "04-udfs/04_udfs_template.ipynb",
        [
            md("# Module 04 — UDF Performance\n\nSerialization cost: Python UDF vs Pandas UDF vs native Spark."),
            code(
                "import sys\nsys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '.')\nfrom shared.spark_session import get_spark\nfrom shared import config\nfrom shared.utils import timed_action\n\nspark = get_spark('module-04-udfs')\ntrips = spark.read.parquet(*config.yellow_taxi_paths())\ndf = trips.select('PULocationID').filter('PULocationID IS NOT NULL').limit(1_000_000)"
            ),
            md("## 1. Vanilla Python UDF\n\nRow-by-row Python callback — highest serialization overhead."),
            code(
                "from pyspark.sql.functions import udf\nfrom pyspark.sql.types import StringType\nimport hashlib\n\n@udf(StringType())\ndef py_hash(val):\n    if val is None:\n        return None\n    return hashlib.md5(str(val).encode()).hexdigest()\n\nresult_py = df.withColumn('h', py_hash('PULocationID'))\n_, t_py = timed_action(result_py)\nprint(f'Python UDF: {t_py:.2f}s')"
            ),
            md("## 2. Pandas UDF (Arrow)\n\nBatch transfer via Apache Arrow — much lower per-row overhead."),
            code(
                "import pandas as pd\nfrom pyspark.sql.functions import pandas_udf\n\n@pandas_udf(StringType())\ndef pandas_hash(series: pd.Series) -> pd.Series:\n    return series.astype(str).apply(lambda x: hashlib.md5(x.encode()).hexdigest())\n\nresult_pandas = df.withColumn('h', pandas_hash('PULocationID'))\n_, t_pandas = timed_action(result_pandas)\nprint(f'Pandas UDF: {t_pandas:.2f}s')"
            ),
            md("## 3. Native Spark SQL\n\nNo Python boundary — fastest."),
            code(
                "from pyspark.sql.functions import sha2, col\n\nresult_native = df.withColumn('h', sha2(col('PULocationID').cast('string'), 256))\n_, t_native = timed_action(result_native)\nprint(f'Native Spark: {t_native:.2f}s')"
            ),
            code(
                "print(f'\\nSpeedup vs Python UDF:')\nprint(f'  Pandas UDF:  {t_py/t_pandas:.1f}x')\nprint(f'  Native:      {t_py/t_native:.1f}x')"
            ),
            md("## Why?\n\n| Approach | Data path | Cost |\n|----------|-----------|------|\n| Python UDF | JVM → pickle → Python (per row) | Highest |\n| Pandas UDF | JVM → Arrow batches → Python | Medium |\n| Native | JVM only | Lowest |\n\nCheck Spark UI **Stages** tab: Python UDF shows `PythonUDF` in the plan."),
            md("## Key Takeaways\n\n1. Prefer native Spark functions whenever possible.\n2. Pandas UDFs are the best choice when custom Python logic is required.\n3. Vanilla Python UDFs are a last resort for performance-critical paths."),
        ],
    )


def module_04_exercise():
    write_nb(
        ROOT / "04-udfs/exercises/04_exercise.ipynb",
        [
            md("# Module 04 — Exercise\n\nRewrite a Python UDF as Pandas UDF and native Spark."),
            code(
                "import sys\nsys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '../..')\nfrom shared.spark_session import get_spark\nfrom shared import config\n\nspark = get_spark('module-04-exercise')\ndf = spark.read.parquet(*config.yellow_taxi_paths()).select('PULocationID', 'DOLocationID').limit(500_000)"
            ),
            code(
                "from pyspark.sql.functions import udf\nfrom pyspark.sql.types import IntegerType\n\n@udf(IntegerType())\ndef location_sum(a, b):\n    if a is None or b is None:\n        return None\n    return int(a) + int(b)\n\n# TODO: rewrite as pandas_udf\n# TODO: rewrite as native Spark (col('PULocationID') + col('DOLocationID'))\n# Time all three approaches\n"
            ),
        ],
    )


def module_05_template():
    write_nb(
        ROOT / "05-shuffle-sort/05_shuffle_sort_template.ipynb",
        [
            md("# Module 05 — Shuffle & Sort\n\nJoin strategies, Storage Partitioned Join (SPJ), and table ordering."),
            code(
                "import sys\nsys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '.')\nfrom shared.spark_session import get_spark\nfrom shared import config\n\nspark = get_spark('module-05-shuffle-sort')\ntrips = spark.read.parquet(*config.yellow_taxi_paths())\nzones = spark.read.option('header', True).csv(config.zones_path())"
            ),
            md("## 1. Broadcast Join"),
            code(
                "spark.conf.set('spark.sql.autoBroadcastJoinThreshold', '50MB')\nsmall = zones.limit(50)\nplan = trips.join(small.withColumnRenamed('LocationID', 'PULocationID'), 'PULocationID')\nplan.explain('formatted')\n# Look for BroadcastHashJoin"
            ),
            md("## 2. Sort-Merge Join (disable broadcast)"),
            code(
                "spark.conf.set('spark.sql.autoBroadcastJoinThreshold', '-1')\nplan = trips.join(zones.withColumnRenamed('LocationID', 'PULocationID'), 'PULocationID')\nplan.explain('formatted')\n# Look for SortMergeJoin + Exchange"
            ),
            md("## 3. Storage Partitioned Join (SPJ)\n\nWhen both Iceberg tables share compatible partitioning, Spark can avoid shuffle."),
            code(
                "spark.sql('''\n    SET spark.sql.sources.v2.bucketing.enabled=true;\n    SET spark.sql.sources.v2.bucketing.pushPartValues.enabled=true;\n    SET spark.sql.iceberg.planning.preserve-data-grouping=true;\n    SET spark.sql.requireAllClusterKeysForCoPartition=false;\n    SET spark.sql.autoBroadcastJoinThreshold=-1;\n''')"
            ),
            code(
                "trips_a = trips.select('VendorID', 'PULocationID', 'total_amount', 'tpep_pickup_datetime')\ntrips_b = trips.select('VendorID', 'DOLocationID', 'total_amount', 'tpep_dropoff_datetime')\n\n# Write two Iceberg tables partitioned identically\ntrips_a.writeTo('local.default.trips_a').using('iceberg').partitionedBy('PULocationID').createOrReplace()\ntrips_b.writeTo('local.default.trips_b').using('iceberg').partitionedBy('PULocationID').createOrReplace()"
            ),
            code(
                "spj = spark.sql('''\n    SELECT a.VendorID, a.total_amount, b.total_amount\n    FROM local.default.trips_a a\n    JOIN local.default.trips_b b\n    ON a.PULocationID = b.PULocationID AND a.VendorID = b.VendorID\n''')\nspj.explain('formatted')\n# With SPJ: no Exchange before join\nspj.limit(10).show()"
            ),
            md("## 4. Table-Level Ordering\n\n`WRITE ORDERED BY` sets `write.distribution-mode=range`, causing sort on write."),
            code(
                "spark.sql('''\n    CREATE OR REPLACE TABLE local.default.trips_ordered\n    USING iceberg\n    AS SELECT * FROM local.default.trips_a\n''')\nspark.sql('ALTER TABLE local.default.trips_ordered WRITE ORDERED BY (PULocationID, total_amount)')\nspark.sql('SHOW TBLPROPERTIES local.default.trips_ordered').filter(\"key LIKE 'write.%' OR key = 'sort-order'\").show(truncate=False)"
            ),
            code(
                "# Write with pre-sorted data, skip table ordering enforcement\nsorted_df = trips_a.orderBy('PULocationID', 'total_amount')\nsorted_df.writeTo('local.default.trips_presorted').using('iceberg') \\\n    .option('use-table-distribution-and-ordering', 'false') \\\n    .createOrReplace()"
            ),
            md("## Key Takeaways\n\n1. Broadcast join avoids shuffle for small tables.\n2. SPJ eliminates shuffle when Iceberg partition specs align.\n3. Table sort order improves read performance but adds write cost."),
        ],
    )


def module_05_exercise():
    write_nb(
        ROOT / "05-shuffle-sort/exercises/05_exercise.ipynb",
        [
            md("# Module 05 — Exercise\n\nCompare join plans with and without SPJ."),
            code(
                "import sys\nsys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '../..')\nfrom shared.spark_session import get_spark\nfrom shared import config\n\nspark = get_spark('module-05-exercise')\ntrips = spark.read.parquet(*config.yellow_taxi_paths())"
            ),
            md("## Task\n\nCreate two Iceberg tables with matching partition columns. Compare `explain('formatted')` with SPJ configs on vs off."),
            code(
                "# TODO: create partitioned tables and run join\n# TODO: capture plan with SPJ enabled and disabled\n"
            ),
        ],
    )


def module_06_template():
    write_nb(
        ROOT / "06-java-gc-gluten/06_java_gc_gluten_template.ipynb",
        [
            md("# Module 06 — Java GC & Gluten\n\nPart A: JVM tuning. Part B: optional Gluten native acceleration."),
            code(
                "import sys\nsys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '.')\nfrom shared.spark_session import get_spark, ui_links\nfrom shared import config\nfrom shared.utils import timed_action\n\nspark = get_spark('module-06-java-gc')\nui_links()"
            ),
            md("## Part A — JVM / GC Tuning\n\nDriver and executor JVMs are separate processes. GC pauses show up in Spark UI **Executors** tab (GC Time column)."),
            code(
                "trips = spark.read.parquet(*config.yellow_taxi_paths())\n\n# Memory-heavy job: wide aggregations trigger object allocation\nheavy = trips.groupBy('PULocationID', 'DOLocationID', 'VendorID').count()\n_, t = timed_action(heavy)\nprint(f'Aggregation completed in {t:.2f}s')\nprint('Check Executors tab → GC Time column at http://localhost:4040')"
            ),
            md("### Current JVM Settings\n\nInspect executor memory and GC config:"),
            code(
                "for item in ['spark.driver.memory', 'spark.executor.memory', 'spark.memory.fraction']:\n    print(f'{item}: {spark.conf.get(item, \"default\")}')"
            ),
            md("### GC Strategies (Java 17+)\n\n| GC | Flag | Best for |\n|----|------|----------|\n| G1 (default) | `-XX:+UseG1GC` | General purpose |\n| ZGC | `-XX:+UseZGC` | Low-latency, large heaps |\n\nTo experiment, set in `docker/spark-defaults.conf`:\n```\nspark.executor.extraJavaOptions  -XX:+UseG1GC -XX:G1HeapRegionSize=16m\nspark.driver.extraJavaOptions    -XX:+UseG1GC\n```\nThen restart the cluster."),
            md("### Key Memory Configs\n\n- `spark.memory.fraction` (default 0.6) — fraction of heap for Spark vs user memory\n- `spark.memory.storageFraction` — cache vs execution memory split\n- OOM symptoms: tasks fail with `OutOfMemoryError`, spill to disk increases"),
            md("## Part B — Gluten (Optional)\n\nGluten offloads Spark operators to native engines (Velox). Requires separate setup.\n\n> **Note:** Gluten 1.7.0 supports Spark 4.1 but excludes Iceberg in preview builds. The Gluten demo uses plain Parquet."),
            code(
                "import os\nGLUTEN_ENABLED = os.environ.get('SPARK_GLUTEN_ENABLED', 'false').lower() == 'true'\nprint(f'Gluten enabled: {GLUTEN_ENABLED}')\n\nif not GLUTEN_ENABLED:\n    print('Start with: make up-gluten (after installing Gluten binaries — see README)')\nelse:\n    bench = spark.read.parquet(*config.yellow_taxi_paths())\n    result = bench.groupBy('PULocationID').agg({'total_amount': 'sum', 'trip_distance': 'avg'})\n    result.explain('formatted')\n    _, t = timed_action(result)\n    print(f'Gluten benchmark: {t:.2f}s')"
            ),
            md("## Key Takeaways\n\n1. Monitor GC Time in Spark UI before tuning JVM flags.\n2. Increase executor memory or partitions before reaching for exotic GC settings.\n3. Gluten can accelerate CPU-bound SQL but requires compatible native libraries and excludes Iceberg today."),
        ],
    )


def module_06_exercise():
    write_nb(
        ROOT / "06-java-gc-gluten/exercises/06_exercise.ipynb",
        [
            md("# Module 06 — Exercise\n\nAnalyze GC impact and document tuning recommendations."),
            code(
                "import sys\nsys.path.insert(0, '/workspace' if __import__('pathlib').Path('/workspace').exists() else '../..')\nfrom shared.spark_session import get_spark\nfrom shared import config\n\nspark = get_spark('module-06-exercise')\ntrips = spark.read.parquet(*config.yellow_taxi_paths())"
            ),
            md("## Task 1\n\nRun a memory-heavy aggregation. Record GC Time from the Executors tab."),
            code(
                "# TODO: run groupBy on 3+ columns, report GC time from UI\nheavy = trips.groupBy('PULocationID', 'DOLocationID', 'VendorID', 'payment_type').count()\nheavy.count()\n"
            ),
            md("## Task 2\n\nWrite 3 tuning recommendations based on your observations (memory, partitions, GC flags)."),
            code("# YOUR ANSWER (markdown cell or print):\n# 1. ...\n# 2. ...\n# 3. ...\n"),
        ],
    )


if __name__ == "__main__":
    module_01_template()
    module_01_exercise()
    module_02_template()
    module_02_exercise()
    module_03_template()
    module_03_exercise()
    module_04_template()
    module_04_exercise()
    module_05_template()
    module_05_exercise()
    module_06_template()
    module_06_exercise()
    print("Done.")
