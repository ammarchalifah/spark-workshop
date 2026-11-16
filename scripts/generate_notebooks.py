#!/usr/bin/env python3
"""Generate all six lab notebooks from module definitions."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

METADATA = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"},
}

BOOT = """import sys
sys.path.insert(0, '/workspace')
from shared.spark_session import begin_module, ui_links, explain_plan
from shared import config
from shared.utils import timed_action, timed_read, drop_iceberg_table, reset_spark_configs
from shared.demo_data import user_post_activity
"""


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
        ROOT / "01-spark-plans/01_spark_plans.ipynb",
        [
            md(
                "# Module 01 — Spark API & Query Plans\n\n"
                "Goals: PySpark DataFrame API vs `spark.sql`, one engine underneath; read plans from logical → physical.\n\n"
                "Open the **Application UI** (host port mapped to container `4040`) before running actions."
            ),
            code(BOOT + "\nspark = begin_module('module-01-spark-plans')\nui_links()"),
            md("## TLC data"),
            code(
                "trips = spark.read.parquet(*config.yellow_taxi_paths())\n"
                "zones = spark.read.option('header', True).csv(config.zones_path())\n"
                "print('trips columns:', len(trips.columns))"
            ),
            md(
                "## PySpark vs Spark SQL — same query\n\n"
                "Spark parses both into a **logical plan**, runs **analyzer** (resolve columns/types), "
                "**optimizer** (rules), then builds a **physical plan** for execution."
            ),
            code(
                "from pyspark.sql import functions as F\n\n"
                "df_api = (\n"
                "    trips.filter(F.col('VendorID').isin(1, 2))\n"
                "    .groupBy('VendorID')\n"
                "    .agg(F.count('*').alias('trips'), F.avg('total_amount').alias('avg_fare'))\n"
                "    .orderBy(F.desc('trips'))\n"
                ")\n"
                "df_api.show(5)"
            ),
            code(
                "df_sql = spark.sql('''\n"
                "    SELECT VendorID, COUNT(*) AS trips, AVG(total_amount) AS avg_fare\n"
                "    FROM parquet.`{}`\n"
                "    WHERE VendorID IN (1, 2)\n"
                "    GROUP BY VendorID\n"
                "    ORDER BY trips DESC\n"
                "'''.format(config.yellow_taxi_paths()[0]))\n"
                "df_sql.show(5)"
            ),
            code(
                "print('--- DataFrame API plan ---')\n"
                "df_api.explain('formatted')\n"
                "print('--- Spark SQL plan ---')\n"
                "df_sql.explain('formatted')"
            ),
            md("## Extended `explain(true)` — plan phases"),
            code("df_api.explain(mode='extended')"),
            md(
                "### Vocabulary\n\n"
                "| Phase | Role |\n"
                "|-------|------|\n"
                "| **Parsed / Logical** | What you asked for |\n"
                "| **Analyzed** | Catalog resolved, types fixed |\n"
                "| **Optimized** | Filter pushdown, column pruning (more in module 02) |\n"
                "| **Physical** | Joins, shuffle, scans chosen for executors |"
            ),
            md("## Example 2 — projection + filter (DataFrame & SQL)"),
            code(
                "narrow_api = trips.select('VendorID', 'total_amount', 'PULocationID').filter('total_amount > 50')\n"
                "narrow_sql = spark.sql(f'''\n"
                "    SELECT VendorID, total_amount, PULocationID\n"
                "    FROM parquet.`{config.yellow_taxi_paths()[0]}`\n"
                "    WHERE total_amount > 50\n"
                "''')\n"
                "explain_plan(narrow_api)\n"
                "narrow_sql.explain('formatted')"
            ),
            md("## Example 3 — join then aggregate"),
            code(
                "from pyspark.sql import functions as F\n"
                "z = zones.withColumnRenamed('LocationID', 'PULocationID')\n"
                "joined_api = trips.join(z, 'PULocationID', 'left')\n"
                "by_borough = joined_api.groupBy('Borough').agg(F.count('*').alias('n'))\n"
                "by_borough.show(5)\n"
                "explain_plan(by_borough)"
            ),
            md(
                "## Spark UI: jobs, stages, tasks\n\n"
                "Run `by_borough.show()` — note the **job** in the UI. Transformations alone only extend the plan."
            ),
            code(
                "spark.conf.set('spark.sql.shuffle.partitions', '8')\n"
                "by_borough.explain('formatted')\n"
                "spark.conf.set('spark.sql.shuffle.partitions', '200')\n"
                "by_borough.explain('formatted')"
            ),
            md(
                "## Takeaways\n\n"
                "1. DataFrame API and Spark SQL converge on the same planner.\n"
                "2. Use `explain('formatted')` in class; `extended` shows analyzer/optimizer output.\n"
                "3. Physical plan + UI connects code to cluster work (modules 02–05 go deeper)."
            ),
        ],
    )


def module_02():
    write_nb(
        ROOT / "02-plan-joins/02_plan_joins.ipynb",
        [
            md(
                "# Module 02 — Optimizer Rules & Join Strategies\n\n"
                "Column pruning, filter pushdown, equi vs inequi joins, and how to read join nodes in `explain`."
            ),
            code(BOOT + "\nfrom pyspark.sql import functions as F\n"
                "spark = begin_module('module-02-plan-joins')\nui_links()"),
            code(
                "trips = spark.read.parquet(*config.yellow_taxi_paths())\n"
                "zones = spark.read.option('header', True).csv(config.zones_path())\n"
                "trips_small = trips.select(\n"
                "    'VendorID', 'PULocationID', 'DOLocationID', 'total_amount', 'tpep_pickup_datetime'\n"
                ")"
            ),
            md("## Column pruning"),
            code(
                "wide = trips  # many columns\n"
                "narrow = trips.select('VendorID', 'total_amount')\n"
                "narrow.explain('formatted')  # fewer Parquet columns read\n"
                "wide.filter('total_amount > 80').select('VendorID').explain('formatted')"
            ),
            md("## Filter pushdown"),
            code(
                "q = trips_small.filter('total_amount > 100 AND VendorID = 2')\n"
                "q.explain('formatted')  # PushedFilters / PostScan filters on Parquet"
            ),
            md("## Equi-join baseline (sort-merge at scale)"),
            code(
                "reset_spark_configs(spark, {\n"
                "    'spark.sql.autoBroadcastJoinThreshold': '-1',\n"
                "    'spark.sql.join.preferSortMergeJoin': 'true',\n"
                "})\n"
                "equi = trips_small.alias('t').join(\n"
                "    trips_small.alias('s'),\n"
                "    (F.col('t.VendorID') == F.col('s.VendorID'))\n"
                "    & (F.col('t.PULocationID') == F.col('s.PULocationID')),\n"
                ")\n"
                "equi.select('t.VendorID', 't.PULocationID').limit(5).explain('formatted')"
            ),
            md("## Broadcast hash join (small dimension)"),
            code(
                "z = zones.withColumnRenamed('LocationID', 'PULocationID')\n"
                "reset_spark_configs(spark, {'spark.sql.autoBroadcastJoinThreshold': '52428800'})\n"
                "bj = trips_small.join(z, 'PULocationID', 'inner')\n"
                "bj.explain('formatted')  # BroadcastExchange / BroadcastHashJoin"
            ),
            md("## Shuffle hash join (disable sort-merge preference)"),
            code(
                "reset_spark_configs(spark, {\n"
                "    'spark.sql.autoBroadcastJoinThreshold': '-1',\n"
                "    'spark.sql.join.preferSortMergeJoin': 'false',\n"
                "})\n"
                "big = trips_small.repartition(32, 'VendorID')\n"
                "shj = big.alias('a').join(big.alias('b'), 'VendorID', 'inner')\n"
                "shj.limit(1).explain('formatted')  # ShuffledHashJoin when chosen"
            ),
            md("## Sort-merge join (default for large equi)"),
            code(
                "reset_spark_configs(spark, {\n"
                "    'spark.sql.autoBroadcastJoinThreshold': '-1',\n"
                "    'spark.sql.join.preferSortMergeJoin': 'true',\n"
                "})\n"
                "smj = big.alias('a').join(big.alias('b'), 'PULocationID', 'inner')\n"
                "smj.limit(1).explain('formatted')  # SortMergeJoin"
            ),
            md("## Cartesian / broadcast nested loop (dangerous at scale)"),
            code(
                "tiny_a = trips_small.select('VendorID').distinct().limit(5)\n"
                "tiny_b = trips_small.select('PULocationID').distinct().limit(5)\n"
                "cross = tiny_a.crossJoin(tiny_b)\n"
                "cross.explain('formatted')\n"
                "spark.conf.set('spark.sql.crossJoin.enabled', 'true')"
            ),
            code(
                "inequi_loop = tiny_a.alias('a').join(\n"
                "    tiny_b.alias('b'),\n"
                "    F.col('a.VendorID') < F.col('b.PULocationID'),\n"
                ")\n"
                "inequi_loop.explain('formatted')  # often BroadcastNestedLoopJoin or Cartesian"
            ),
            md(
                "## Inequi join challenge — decompose to equi + filter\n\n"
                "Predicate: match trips whose `total_amount` is within $5 (range / inequi).\n"
                "Instead of `abs(t-s) < 5` in the join, **bucket** amounts and join on equi keys, then filter."
            ),
            code(
                "a = trips_small.select('VendorID', 'total_amount').withColumn(\n"
                "    'amt_bucket', F.floor(F.col('total_amount') / 5)\n"
                ")\n"
                "b = a.select(\n"
                "    F.col('VendorID').alias('v2'),\n"
                "    F.col('total_amount').alias('amt_b'),\n"
                "    F.col('amt_bucket').alias('b_bucket'),\n"
                ")\n"
                "equi_buckets = a.join(\n"
                "    b,\n"
                "    (F.col('VendorID') == F.col('v2')) & (F.col('amt_bucket') == F.col('b_bucket')),\n"
                ")\n"
                "refined = equi_buckets.filter(\n"
                "    F.abs(F.col('total_amount') - F.col('amt_b')) <= 5\n"
                ")\n"
                "refined.limit(5).explain('formatted')\n"
                "print('rows (capped action):', refined.limit(1000).count())"
            ),
            md(
                "## Takeaways\n\n"
                "1. Prune columns and push filters early — check `explain`.\n"
                "2. Equi joins map to BHJ / SHJ / SMJ; inequi often explodes (BNLJ / cartesian).\n"
                "3. Rewrite inequi as equi + residual filter when possible."
            ),
        ],
    )


def module_03():
    write_nb(
        ROOT / "03-storage-io/03_storage_io.ipynb",
        [
            md(
                "# Module 03 — Storage I/O, Types & Iceberg (DSv2)\n\n"
                "Compare formats and schemas, then a full Iceberg walkthrough: snapshots, time travel, partition evolution, and on-disk growth + compaction."
            ),
            code(BOOT + "\nspark = begin_module('module-03-storage-io')\nui_links()"),
            code(
                "from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType\n"
                "trips = spark.read.parquet(*config.yellow_taxi_paths())\n"
                "sample = trips.select(\n"
                "    'VendorID', 'PULocationID', 'total_amount', 'tpep_pickup_datetime'\n"
                ").limit(200_000)\n"
                "out = config.OUTPUT_BASE / '03-formats'\n"
                "out.mkdir(parents=True, exist_ok=True)"
            ),
            md("## Write all formats"),
            code(
                "sample.write.mode('overwrite').json(str(out / 'json'))\n"
                "sample.write.mode('overwrite').option('header', True).csv(str(out / 'csv'))\n"
                "sample.write.mode('overwrite').parquet(str(out / 'parquet'))\n"
                "drop_iceberg_table(spark, 'local.default.io_lab_sample')\n"
                "sample.writeTo('local.default.io_lab_sample').using('iceberg').create()"
            ),
            md("## Read benchmarks (count)"),
            code(
                "results = {}\n"
                "_, results['json'] = timed_read(spark, lambda: spark.read.json(str(out / 'json')))\n"
                "_, results['csv'] = timed_read(\n"
                "    spark, lambda: spark.read.option('header', True).schema(sample.schema).csv(str(out / 'csv'))\n"
                ")\n"
                "_, results['parquet'] = timed_read(spark, lambda: spark.read.parquet(str(out / 'parquet')))\n"
                "_, results['iceberg'] = timed_read(spark, lambda: spark.table('local.default.io_lab_sample'))\n"
                "for k, t in sorted(results.items(), key=lambda x: -x[1]):\n"
                "    print(f'{k:10s} {t:.2f}s')"
            ),
            md("## Type safety — CSV without schema"),
            code(
                "bad_csv = spark.read.option('header', True).csv(str(out / 'csv'))\n"
                "bad_csv.printSchema()  # many strings\n"
                "typed_csv = spark.read.schema(sample.schema).option('header', True).csv(str(out / 'csv'))\n"
                "typed_csv.printSchema()"
            ),
            md("## Type safety — JSON inference"),
            code(
                "infer_json = spark.read.json(str(out / 'json'))\n"
                "infer_json.printSchema()\n"
                "strict_json = spark.read.schema(sample.schema).json(str(out / 'json'))\n"
                "strict_json.printSchema()"
            ),
            md(
                "## Iceberg deep dive (single table)\n\n"
                "Table `local.default.workshop_iceberg` — **DataSource V2**, snapshot isolation, hidden partitioning, metadata tree under `data/output/warehouse/`."
            ),
            code(
                "ICEBERG = 'local.default.workshop_iceberg'\n"
                "SHORT = 'workshop_iceberg'\n\n"
                "def iceberg_storage_stats(short: str) -> dict:\n"
                "    root = config.WAREHOUSE_DIR / 'default' / short\n"
                "    if not root.exists():\n"
                "        return {'data_files': 0, 'data_mb': 0.0, 'metadata_mb': 0.0, 'total_mb': 0.0}\n"
                "    data = list((root / 'data').rglob('*.parquet')) if (root / 'data').exists() else []\n"
                "    meta = list((root / 'metadata').rglob('*')) if (root / 'metadata').exists() else []\n"
                "    data_b = sum(p.stat().st_size for p in data)\n"
                "    meta_b = sum(p.stat().st_size for p in meta if p.is_file())\n"
                "    return {\n"
                "        'data_files': len(data),\n"
                "        'data_mb': data_b / 1e6,\n"
                "        'metadata_mb': meta_b / 1e6,\n"
                "        'total_mb': (data_b + meta_b) / 1e6,\n"
                "    }\n\n"
                "def print_storage(label: str, stats: dict) -> None:\n"
                "    print(\n"
                "        f\"{label}: {stats['data_files']} data files, \"\n"
                "        f\"data {stats['data_mb']:.2f} MB, metadata {stats['metadata_mb']:.2f} MB, \"\n"
                "        f\"total {stats['total_mb']:.2f} MB\"\n"
                "    )\n\n"
                "def snapshot_ids(limit: int = 20):\n"
                "    return spark.sql(\n"
                "        f'SELECT snapshot_id, parent_id, committed_at FROM {ICEBERG}.snapshots '\n"
                "        'ORDER BY committed_at'\n"
                "    ).limit(limit).collect()"
            ),
            md("### Step 1 — initial load (partitioned table)"),
            code(
                "drop_iceberg_table(spark, ICEBERG)\n"
                "initial = sample.repartition(4).cache()\n"
                "(\n"
                "    initial.writeTo(ICEBERG)\n"
                "    .using('iceberg')\n"
                "    .partitionedBy('PULocationID')\n"
                "    .create()\n"
                ")\n"
                "stats_initial = iceberg_storage_stats(SHORT)\n"
                "print_storage('After initial create', stats_initial)\n"
                "spark.sql(f'SELECT snapshot_id, summary FROM {ICEBERG}.snapshots').show(truncate=False)\n"
                "snap_create = snapshot_ids()[-1].snapshot_id\n"
                "rows_create = spark.table(ICEBERG).count()\n"
                "print(f'snapshot {snap_create} row count: {rows_create:,}')"
            ),
            md(
                "### Step 2 — mutate data (new snapshots)\n\n"
                "Append rows, then **delete** — each commit adds a snapshot you can time-travel to."
            ),
            code(
                "extra = sample.limit(25_000).repartition(8)\n"
                "extra.writeTo(ICEBERG).using('iceberg').append()\n"
                "snap_after_append = snapshot_ids()[-1].snapshot_id\n"
                "print_storage('After append', iceberg_storage_stats(SHORT))\n\n"
                "spark.sql(f'''\n"
                "    DELETE FROM {ICEBERG}\n"
                "    WHERE VendorID = 2 AND total_amount > 75\n"
                "''')\n"
                "snap_after_delete = snapshot_ids()[-1].snapshot_id\n"
                "print_storage('After delete', iceberg_storage_stats(SHORT))\n"
                "spark.sql(f'SELECT snapshot_id, committed_at FROM {ICEBERG}.snapshots ORDER BY committed_at').show()"
            ),
            md("### Step 3 — time travel"),
            code(
                "def count_at_snapshot(snap_id: int) -> int:\n"
                "    return spark.sql(f'SELECT COUNT(*) AS n FROM {ICEBERG} VERSION AS OF {snap_id}').collect()[0].n\n\n"
                "for label, sid in [\n"
                "    ('create', snap_create),\n"
                "    ('after append', snap_after_append),\n"
                "    ('after delete', snap_after_delete),\n"
                "    ('current', None),\n"
                "]:\n"
                "    if sid is None:\n"
                "        n = spark.table(ICEBERG).count()\n"
                "    else:\n"
                "        n = count_at_snapshot(sid)\n"
                "    print(f'{label}: snapshot={sid} rows={n:,}')\n\n"
                "# DataFrame reader variant\n"
                "spark.read.option('snapshot-id', str(snap_create)).table(ICEBERG).count()"
            ),
            md(
                "### Step 4 — partition evolution\n\n"
                "Add a **new hidden partition field** — metadata only; old files keep the old spec, new writes use the new spec."
            ),
            code(
                "spark.sql(f'DESCRIBE TABLE EXTENDED {ICEBERG}').filter(\n"
                "    \"col_name LIKE '%Partition%' or col_name = 'Provider'\"\n"
                ").show(truncate=False)\n"
                "spark.sql(f'SELECT * FROM {ICEBERG}.partitions').show(10, truncate=False)"
            ),
            code(
                "spark.sql(f'ALTER TABLE {ICEBERG} ADD PARTITION FIELD bucket(16, VendorID)')\n"
                "print('Added bucket(16, VendorID) — new appends land in evolved layout')\n"
                "evo_batch = sample.limit(30_000).repartition(16, 'VendorID')\n"
                "evo_batch.writeTo(ICEBERG).using('iceberg').append()\n"
                "print_storage('After partition evolution + append', iceberg_storage_stats(SHORT))\n"
                "spark.sql(f'SELECT partition, spec_id, record_count, file_count FROM {ICEBERG}.partitions').show(\n"
                "    15, truncate=False\n"
                ")"
            ),
            md(
                "### Step 5 — repeated small writes (file sprawl)\n\n"
                "Many tiny commits → more data files + metadata; compare volume before/after compaction."
            ),
            code(
                "tiny = sample.limit(3_000)\n"
                "for i in range(6):\n"
                "    tiny.repartition(4).writeTo(ICEBERG).using('iceberg').append()\n"
                "stats_before_compact = iceberg_storage_stats(SHORT)\n"
                "print_storage('After repeated small appends', stats_before_compact)"
            ),
            code(
                "spark.sql('''\n"
                "    CALL local.system.rewrite_data_files(\n"
                "        table => 'default.workshop_iceberg',\n"
                "        strategy => 'binpack',\n"
                "        options => map(\n"
                "            'rewrite-all', 'true',\n"
                "            'min-input-files', '2'\n"
                "        )\n"
                "    )\n"
                "''').show(truncate=False)"
            ),
            code(
                "stats_final = iceberg_storage_stats(SHORT)\n"
                "print_storage('After rewrite_data_files', stats_final)\n"
                "print('\\nSummary')\n"
                "for phase, st in [\n"
                "    ('1 initial', stats_initial),\n"
                "    ('2 after sprawl', stats_before_compact),\n"
                "    ('3 after compaction', stats_final),\n"
                "]:\n"
                "    print_storage(phase, st)\n"
                "wh = config.WAREHOUSE_DIR / 'default' / SHORT\n"
                "print('warehouse path:', wh)\n"
                "print('sample files:')\n"
                "for p in sorted(wh.rglob('*'))[:25]:\n"
                "    if p.is_file():\n"
                "        print(f\"  {p.relative_to(wh)}  ({p.stat().st_size / 1e3:.1f} KB)\")"
            ),
            md(
                "## Takeaways\n\n"
                "1. Parquet/Iceberg win on analytics reads; enforce schemas on CSV/JSON.\n"
                "2. **Snapshots** enable time travel (`VERSION AS OF` / `snapshot-id`).\n"
                "3. **Partition evolution** changes layout for new files only.\n"
                "4. Track **data vs metadata** footprint; compact with `rewrite_data_files` when file count explodes."
            ),
        ],
    )


def module_04():
    write_nb(
        ROOT / "04-lazy-execution/04_lazy_execution.ipynb",
        [
            md("# Module 04 — Lazy Evaluation, Actions & Reuse"),
            code(BOOT + "\nspark = begin_module('module-04-lazy-execution')\nui_links()"),
            code(
                "from pyspark.sql import functions as F, Window\n"
                "trips = spark.read.parquet(*config.yellow_taxi_paths())\n"
                "expensive = (\n"
                "    trips.filter('total_amount > 10')\n"
                "    .withColumn('rn', F.row_number().over(Window.partitionBy('VendorID').orderBy(F.desc('total_amount'))))\n"
                "    .filter('rn <= 100')\n"
                "    .groupBy('PULocationID')\n"
                "    .agg(F.avg('total_amount').alias('avg_fare'), F.count('*').alias('n'))\n"
                ")\n"
                "expensive.explain('formatted')"
            ),
            md("## Each action can trigger a new job"),
            code(
                "_, t1 = timed_action(expensive)\n"
                "_, t2 = timed_action(expensive, action='collect')\n"
                "print(f'count={t1:.2f}s, collect={t2:.2f}s — check UI job list')"
            ),
            md("## Branching DAG — duplicate work"),
            code(
                "branch_a = expensive.filter('n > 50')\n"
                "branch_b = expensive.filter('avg_fare > 30')\n"
                "_, ta = timed_action(branch_a)\n"
                "_, tb = timed_action(branch_b)\n"
                "print(f'without cache: a={ta:.2f}s b={tb:.2f}s (shared ancestor recomputed)')"
            ),
            md("## Spark Observation (metrics without double full scan for logging)"),
            code(
                "from pyspark.sql import Observation\n"
                "obs = Observation('avg_rows')\n"
                "observed = trips.filter('total_amount > 50').observe(obs, F.count(F.lit(1)).alias('rows'))\n"
                "observed.limit(1).collect()  # minimal action to run pipeline\n"
                "print('observed rows metric:', obs.get('rows'))"
            ),
            md("## cache / persist"),
            code(
                "expensive.cache()\n"
                "_, c1 = timed_action(expensive)\n"
                "_, c2 = timed_action(expensive.filter('n > 10'))\n"
                "expensive.unpersist()\n"
                "print(f'with cache: first={c1:.2f}s second={c2:.2f}s')"
            ),
            md("## checkpoint — cuts lineage (serialization cost)"),
            code(
                "ckpt_dir = str(config.CHECKPOINT_DIR)\n"
                "spark.sparkContext.setCheckpointDir(ckpt_dir)\n"
                "ck = expensive.checkpoint(eager=True)\n"
                "ck.explain('formatted')\n"
                "_, tc = timed_action(ck)\n"
                "print(f'checkpointed action: {tc:.2f}s')"
            ),
            md("## Intermediate Iceberg table vs cache"),
            code(
                "drop_iceberg_table(spark, 'local.default.lazy_intermediate')\n"
                "expensive.writeTo('local.default.lazy_intermediate').using('iceberg').create()\n"
                "from_table = spark.table('local.default.lazy_intermediate')\n"
                "from_table.explain('formatted')  # file scan + stats, fresh optimizer view\n"
                "_, tt = timed_action(from_table)\n"
                "print(f'read table: {tt:.2f}s')"
            ),
            md(
                "## Takeaways\n\n"
                "1. Lazy until action; branching without reuse is expensive.\n"
                "2. Observation for metrics; cache/checkpoint for reuse; table for stats + longevity."
            ),
        ],
    )


def module_05():
    write_nb(
        ROOT / "05-data-locality/05_data_locality.ipynb",
        [
            md("# Module 05 — Data Locality, Shuffle & SPJ"),
            code(BOOT + "\nspark = begin_module('module-05-data-locality')\nui_links()"),
            md("## Why shuffle appears"),
            code(
                "from pyspark.sql import functions as F, Window\n"
                "trips = spark.read.parquet(*config.yellow_taxi_paths())\n"
                "agg = trips.groupBy('PULocationID', 'VendorID').count()\n"
                "agg.explain('formatted')  # Exchange\n"
                "w = Window.partitionBy('VendorID').orderBy(F.desc('total_amount'))\n"
                "win = trips.withColumn('rk', F.row_number().over(w))\n"
                "win.limit(1).explain('formatted')"
            ),
            md("## Query shape — keep join keys in aggregation"),
            code(
                "users, events = user_post_activity(spark)\n"
                "joined = events.join(users, 'user_id')\n"
                "bad = joined.groupBy('post_id').count()  # may reshuffle post_id alone\n"
                "good = joined.groupBy('post_id', 'user_id').count()  # aligned with join key\n"
                "bad.explain('formatted')\n"
                "good.explain('formatted')"
            ),
            md("## Join hints"),
            code(
                "zones = spark.read.option('header', True).csv(config.zones_path())\n"
                "z = zones.withColumnRenamed('LocationID', 'PULocationID')\n"
                "from pyspark.sql.functions import broadcast\n"
                "hinted = trips.join(broadcast(z), 'PULocationID', 'inner')\n"
                "hinted.limit(1).explain('formatted')"
            ),
            md("## Storage Partitioned Join — setup"),
            code(
                "spark.conf.set('spark.sql.sources.v2.bucketing.enabled', 'true')\n"
                "spark.conf.set('spark.sql.sources.v2.bucketing.pushPartValues.enabled', 'true')\n"
                "spark.conf.set('spark.sql.iceberg.planning.preserve-data-grouping', 'true')\n"
                "spark.conf.set('spark.sql.requireAllClusterKeysForCoPartition', 'false')\n"
                "spark.conf.set('spark.sql.autoBroadcastJoinThreshold', '-1')\n\n"
                "base = trips.select('VendorID', 'PULocationID', 'total_amount')\n"
                "drop_iceberg_table(spark, 'local.default.spj_a')\n"
                "drop_iceberg_table(spark, 'local.default.spj_b')\n"
                "base.writeTo('local.default.spj_a').using('iceberg').partitionedBy('PULocationID').create()\n"
                "base.writeTo('local.default.spj_b').using('iceberg').partitionedBy('PULocationID').create()"
            ),
            md("### Vanilla SPJ"),
            code(
                "spj = spark.sql('''SELECT a.VendorID, a.total_amount, b.total_amount AS amt_b\n"
                "    FROM local.default.spj_a a JOIN local.default.spj_b b\n"
                "    ON a.PULocationID = b.PULocationID AND a.VendorID = b.VendorID''')\n"
                "spj.explain('formatted')  # no Exchange before join = success"
            ),
            md("### SPJ off — Exchange returns"),
            code(
                "spark.conf.set('spark.sql.sources.v2.bucketing.enabled', 'false')\n"
                "no_spj = spark.sql('''SELECT a.VendorID FROM local.default.spj_a a JOIN local.default.spj_b b\n"
                "    ON a.PULocationID = b.PULocationID AND a.VendorID = b.VendorID''')\n"
                "no_spj.explain('formatted')\n"
                "spark.conf.set('spark.sql.sources.v2.bucketing.enabled', 'true')"
            ),
            md(
                "### One-sided SPJ (only one table partition-aligned)\n\n"
                "Join Iceberg partitioned table to ad-hoc Parquet — expect shuffle on the unclustered side."
            ),
            code(
                "side_path = str(config.OUTPUT_BASE / '05-side.parquet')\n"
                "base.write.mode('overwrite').parquet(side_path)\n"
                "side = spark.read.parquet(side_path)\n"
                "mixed = spark.table('local.default.spj_a').join(side, ['PULocationID', 'VendorID'])\n"
                "mixed.limit(1).explain('formatted')"
            ),
            md("## Takeaways\n\n1. Exchange marks shuffle — agg/join/window often need it.\n2. Align agg keys with prior join keys when possible.\n3. SPJ when both inputs share partition layout; compare with bucketing disabled."),
        ],
    )


def module_06():
    write_nb(
        ROOT / "06-udfs/06_udfs.ipynb",
        [
            md("# Module 06 — UDFs & Planner Visibility"),
            code(BOOT + "\nspark = begin_module('module-06-udfs')\nui_links()"),
            code(
                "from pyspark.sql.functions import udf, col, when, length\n"
                "from pyspark.sql.types import DoubleType\n"
                "trips = spark.read.parquet(*config.yellow_taxi_paths())\n"
                "df = trips.select('PULocationID', 'total_amount').filter('PULocationID IS NOT NULL').limit(500_000)"
            ),
            md("## Python UDF — opaque to optimizer"),
            code(
                "@udf(DoubleType())\n"
                "def fare_tax_py(amount):\n"
                "    return float(amount) * 1.08 if amount else 0.0\n\n"
                "ud = df.withColumn('fare_taxed', fare_tax_py(col('total_amount')))\n"
                "ud.explain('formatted')  # BatchEvalPython / no predicate pushdown through UDF"
            ),
            md("## Native expression — same logic, optimizable"),
            code(
                "native = df.withColumn('fare_taxed', col('total_amount') * 1.08)\n"
                "native.filter('fare_taxed > 50').explain('formatted')"
            ),
            md("## Benchmark"),
            code(
                "_, t_udf = timed_action(ud.select('fare_taxed'))\n"
                "_, t_native = timed_action(native.select('fare_taxed'))\n"
                "print(f'Python UDF: {t_udf:.2f}s')\n"
                "print(f'native:     {t_native:.2f}s')"
            ),
            md("## Pandas UDF (Arrow vectorized)"),
            code(
                "import pandas as pd\n"
                "from pyspark.sql.functions import pandas_udf\n\n"
                "@pandas_udf(DoubleType())\n"
                "def fare_tax_pandas(s: pd.Series) -> pd.Series:\n"
                "    return s * 1.08\n\n"
                "pd_df = df.withColumn('fare_taxed', fare_tax_pandas(col('total_amount')))\n"
                "_, t_pd = timed_action(pd_df.select('fare_taxed'))\n"
                "print(f'pandas UDF: {t_pd:.2f}s')"
            ),
            md(
                "## Takeaways\n\n"
                "1. UDFs block many optimizer rules — compare explain trees.\n"
                "2. Cost = Python round-trip per batch (or per row) + serialization.\n"
                "3. Prefer native functions; Pandas UDF when vectorized Python is required."
            ),
        ],
    )


def main():
    module_01()
    module_02()
    module_03()
    module_04()
    module_05()
    module_06()
    print("Done.")


if __name__ == "__main__":
    main()