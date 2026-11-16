# Module coverage matrix

Maps **rehearsal feedback** and the **new six-module curriculum** to concrete notebook sections. Use this before editing notebooks: every row must reach **Planned** (and later **Done**).

**Legend — current repo (**`main` **notebooks):**

| Status | Meaning |
|--------|---------|
| **None** | Not covered today |
| **Partial** | Mentioned or one demo; not teachable end-to-end |
| **Full** | Covered with examples; may still need depth per new brief |

**Legend — delivery:**

| Column | Purpose |
|--------|---------|
| **Target notebook** | File to extend or replace |
| **Suggested sections** | Outline only (not committed content yet) |

**Module folders (implemented):**

| # | Folder | Notebook |
|---|--------|----------|
| 1 | `01-spark-plans/` | `01_spark_plans.ipynb` |
| 2 | `02-plan-joins/` | `02_plan_joins.ipynb` |
| 3 | `03-storage-io/` | `03_storage_io.ipynb` |
| 4 | `04-lazy-execution/` | `04_lazy_execution.ipynb` |
| 5 | `05-data-locality/` | `05_data_locality.ipynb` |
| 6 | `06-udfs/` | `06_udfs.ipynb` |

Regenerate notebooks after editing `scripts/generate_notebooks.py`: `python3 scripts/generate_notebooks.py`.

---

## Module 1 — Spark foundations (PySpark ↔ Spark SQL + query plans)

| ID   | Learning point (from request)                                                        | Current | Target notebook            | Suggested sections                                                                    | Priority |
| ---- | ------------------------------------------------------------------------------------ | ------- | -------------------------- | ------------------------------------------------------------------------------------- | -------- |
| 1.1  | Same query expressed in **PySpark DataFrame API** and `spark.sql`                    | Partial | `01_how_spark_works.ipynb` | Side-by-side: filter/agg/join; same `explain()`                                       | P0       |
| 1.2  | Prove both paths share **one execution model** (Catalyst / same physical plan shape) | Partial | same                       | `explain("formatted")` / `toLogicalPlan` discussion; optional `parsed` vs `optimized` | P0       |
| 1.3  | **Logical plan** — unresolved vs analyzed                                            | None    | same                       | `explain(true)` or Spark UI SQL tab; vocabulary card                                  | P0       |
| 1.4  | **Analyzer** — resolve names, types, views                                           | None    | same                       | Missing column error → analyzer; catalog `local.`*                                    | P1       |
| 1.5  | **Optimizer** — rule-based rewrites (preview only; detail in Mod 2)                  | Partial | same                       | Tease: “optimizer runs here”; don’t duplicate Mod 2                                   | P1       |
| 1.6  | **Physical plan** — what executors run                                               | Partial | same                       | Link plan to **Jobs / Stages / Tasks** in UI                                          | P0       |
| 1.7  | **Actions vs transformations** (minimal; Mod 4 goes deep)                            | Partial | same                       | One `count` vs `filter`; defer branching DAG                                          | P2       |
| 1.8  | **Driver / executors / partitions** vocabulary                                       | Partial | same                       | Tie partition count to tasks in UI                                                    | P1       |
| 1.9  | Multiple **worked examples** (not one pipeline)                                      | Partial | same                       | ≥3: projection+filter; agg; simple join                                               | P0       |
| 1.10 | Instructor narrative: *when to use SQL vs DataFrame*                                 | None    | README + nb markdown       | DSL vs SQL ergonomics; not performance                                                | P2       |

**Module 1 exit criteria:** Learner can write one query two ways and read `explain("formatted")` through logical → physical names without conflating with join strategy details.

---

## Module 2 — Plan optimization & joins

| ID | Learning point | Current | Target notebook | Suggested sections | Priority |
|----|----------------|---------|-----------------|-------------------|----------|
| 2.1 | **Column pruning / limited column selection** (scan fewer columns) | Partial | *new* `02_plan_joins.ipynb` (or renumber) | `select` on wide Parquet; compare scan metrics / plan | P0 |
| 2.2 | **Filter pushdown** — predicates near scan | Partial | same | `filter` before/after `select`; explain `PushedFilters` / iceberg/parquet | P0 |
| 2.3 | **Partition pruning** (file/table layout) — tie to Mod 3 | None | same | Optional cross-ref Iceberg partition spec | P2 |
| 2.4 | **Equi-join** definition + when planner prefers each strategy | Partial | same | `ON a.k = b.k` only in first pass | P0 |
| 2.5 | **Inequi-join** definition + planner pain | None | same | range / `>` conditions; bad plans, shuffle growth | P0 |
| 2.6 | **Inequi workaround:** two **equi** joins (request pattern) | None | same | Semi/anti or double equi story; worked example | P0 |
| 2.7 | **Broadcast Hash Join (BHJ)** — conditions + `explain` | Partial | today in 05 | Small table; `autoBroadcastJoinThreshold`; disable others | P0 |
| 2.8 | **Sort-Merge Join (SMJ)** — large/large equi | Partial | same | Default at scale; `sort` in plan | P0 |
| 2.9 | **Shuffle Hash Join (SHJ)** — when SMJ/BHJ not chosen | Partial | same | Config / `preferSortMergeJoin`; show in plan | P0 |
| 2.10 | **Cartesian / Broadcast Nested Loop Join (BNLJ)** — when & cost | None | same | Cross join; inequi / no condition; `cartesian` guard config | P0 |
| 2.11 | **BLNJ** — broadcast nested loop join variant in explain | None | same | Distinguish BNL vs cartesian product in UI text | P1 |
| 2.12 | Side-by-side **plan comparison table** (all strategies) | None | same | Markdown + 1 dataset,多个 join shapes | P0 |
| 2.13 | **AQE** — brief (skew, coalesce) optional | Partial | same | `spark.sql.adaptive.enabled` already on | P2 |
| 2.14 | ≥2 datasets / join shapes per strategy | Partial | same | TLC trips + zones; synthetic skew optional | P0 |

**Module 2 exit criteria:** Learner can name join type from `explain`, state equi vs inequi, and sketch inequi → two equi rewrites.

---

## Module 3 — Storage I/O, type safety, Iceberg (DSv2)

| ID   | Learning point                                                      | Current | Target notebook       | Suggested sections                                          | Priority |
| ---- | ------------------------------------------------------------------- | ------- | --------------------- | ----------------------------------------------------------- | -------- |
| 3.1  | **Read/write JSON** — schema inference risk                         | Partial | `03_storage_io.ipynb` | Infer vs explicit schema                                    | P0       |
| 3.2  | **Read/write CSV** — options, parsing cost                          | Partial | same                  | Header, escape; benchmark row                               | P0       |
| 3.3  | **Read/write Parquet** — columnar, pushdown                         | Partial | same                  | `timed_read`; compare to JSON                               | P0       |
| 3.4  | **Iceberg table** read/write via catalog                            | Full    | same                  | `writeTo` / `read`; keep `drop_iceberg_table` pattern       | P0       |
| 3.5  | **Read/write benchmark** (same logical dataset, all formats)        | Partial | same                  | Table of seconds; discuss fairness (repartition, row count) | P0       |
| 3.6  | **Type safety on write** — failures / coercion                      | None    | same                  | Bad CSV row; JSON all-string                                | P0       |
| 3.7  | **Type safety on read** — explicit `schema=` fix                    | None    | same                  | `StructType`; CSV + JSON exercises                          | P0       |
| 3.8  | Intro **DataSource V2** — Spark ↔ table catalog abstraction         | None    | same                  | Iceberg as V2 source; not file-only                         | P1       |
| 3.9  | **Iceberg table layout** on disk — `metadata/`, snapshots           | None    | same                  | `data/output/warehouse/...`; list files                     | P0       |
| 3.10 | **Metadata json** — `*.metadata.json`                               | None    | same                  | Show current snapshot id                                    | P1       |
| 3.11 | **Manifests** — `*.avro` manifest files                             | None    | same                  | What manifest lists (data files)                            | P1       |
| 3.12 | **Snapshots** — time travel / history                               | None    | same                  | `snapshots` metadata table or `history`                     | P1       |
| 3.13 | **Small files problem** — why compaction matters                    | None    | same                  | Many commits / files; read perf                             | P0       |
| 3.14 | **Compaction** — `rewrite_data_files` or `CALL` (Spark 4 + Iceberg) | None    | same                  | Before/after file count                                     | P0       |
| 3.15 | Link compaction to **Mod 5** SPJ (co-located reads)                 | None    | cross-ref             | Partition spec + sorted runs                                | P2       |

**Module 3 exit criteria:** Learner explains format tradeoffs, fixes read types with schema, and describes metadata → manifest → data file + why compact.

---

## Module 4 — Lazy execution, actions, reuse

| ID   | Learning point                                                    | Current | Target notebook           | Suggested sections                                     | Priority |
| ---- | ----------------------------------------------------------------- | ------- | ------------------------- | ------------------------------------------------------ | -------- |
| 4.1  | **Lazy transformations** — no job until action                    | Full    | `02_lazy_execution.ipynb` | Keep or move to `04_`* after renumber                  | P0       |
| 4.2  | Each **action triggers job(s)** — `count`, `show`, `write` differ | Partial | same                      | Run 3 actions; job count in UI                         | P0       |
| 4.3  | **Branching DAG** — duplicate work without cache                  | Partial | same                      | Two actions on shared expensive subtree                | P0       |
| 4.4  | **SparkObservation** — metrics without extra full `count`         | Partial | same                      | `observe` API; log row count progress                  | P0       |
| 4.5  | `cache` **/** `persist` — storage level; planner sees lineage     | Partial | same                      | `explain` before/after; STORAGE on plan                | P0       |
| 4.6  | `checkpoint` — truncates lineage; HDFS/dir cost                   | Partial | same                      | Warning re local vs cluster path (already hit in runs) | P0       |
| 4.7  | **Serialization cost** — cache/checkpoint materialize bytes       | None    | same                      | Time cache vs recompute; storage tab                   | P1       |
| 4.8  | **Intermediate table (Iceberg/Parquet)** vs cache                 | None    | same                      | Stats / CTAS; optimizer can prune again                | P0       |
| 4.9  | **Stats loss** — when cache blocks file stats / size estimates    | None    | same                      | Contrast `spark.table` vs cached DF                    | P1       |
| 4.10 | Decision rubric: observation vs cache vs checkpoint vs table      | None    | same                      | Instructor checklist markdown                          | P0       |
| 4.11 | Multiple examples (≥2 pipelines)                                  | Partial | same                      | Window + agg branch                                    | P0       |

**Module 4 exit criteria:** Learner picks mitigation for a branched DAG and states tradeoff vs materialized table.

---

## Module 5 — Data locality, shuffle, SPJ

| ID | Learning point | Current | Target notebook | Suggested sections | Priority |
|----|----------------|---------|-----------------|-------------------|----------|
| 5.1 | **Why shuffle** — join, agg, window need **distribution** | Partial | `05_shuffle_sort.ipynb` | `Exchange` in plan; map stage boundaries | P0 |
| 5.2 | **Aggregation** — `groupBy` shuffle keys | Partial | same | Hash partitions by key | P0 |
| 5.3 | **Window** — partitionBy + orderBy shuffle/sort | Partial | same | Single vs multiple partitions | P0 |
| 5.4 | **Join** — key redistribution | Partial | same | Cross-ref Mod 2 strategies | P1 |
| 5.5 | **Avoid unnecessary shuffle** — query shape (request example) | None | same | Join on `user_id` then agg on `(post_id, user_id)` not `post_id` alone | P0 |
| 5.6 | **Join hints** — `broadcast`, `shuffle_hash`, `merge` (version-aware) | Partial | same | Force plan; compare to default | P0 |
| 5.7 | **Storage Partitioned Join (SPJ)** — no `Exchange` signal | Partial | same | Iceberg bucket/partition align | P0 |
| 5.8 | **Vanilla SPJ** — partition keys match join keys | Partial | same | `trips_a` / `trips_b` | P0 |
| 5.9 | **SPJ on compatible transform** — e.g. bucketing/transform spec | None | same | Iceberg partition transform docs + config | P0 |
| 5.10 | **One-sided SPJ** — one table clustered, one not | None | same | When optimizer can/cannot push | P0 |
| 5.11 | SPJ configs recap (`v2.bucketing`, preserve grouping, etc.) | Partial | same | SPJ on vs off comparison cell | P0 |
| 5.12 | **Table sort order / clustering** (write ordering) | Partial | same | `WRITE ORDERED BY` | P1 |
| 5.13 | Multiple case studies (≥3) | Partial | same | Hint vs reshape vs SPJ | P0 |

**Module 5 exit criteria:** Learner explains shuffle cause, applies one hint/reshape, and reads SPJ success/failure from plan.

---

## Module 6 — UDFs and planner visibility

| ID | Learning point | Current | Target notebook | Suggested sections | Priority |
|----|----------------|---------|-----------------|-------------------|----------|
| 6.1 | **Python UDF** — opaque to optimizer | Partial | `04_udfs.ipynb` | `explain` shows `BatchEvalPython` / no pushdown | P0 |
| 6.2 | **Suboptimal plan** — filter/agg can't fold through UDF | None | same | Filter below UDF vs native expr | P0 |
| 6.3 | Slow because **row-by-row** Python | Partial | same | Micro-benchmark | P0 |
| 6.4 | Slow because **serialize / deserialize** (Python ↔ JVM) | Partial | same | Compare to JVM columnar | P0 |
| 6.5 | **Pandas UDF (Arrow)** — vectorized batch | Partial | same | `GROUPED_MAP` or scalar pandas | P0 |
| 6.6 | **Native rewrite** — replace UDF with built-ins | Partial | same | `when`/`substring`/`regexp` etc. | P0 |
| 6.7 | When UDF is **justified** (library gap) | None | same | Short decision tree | P1 |
| 6.8 | ≥3 examples (Python UDF → Pandas → native) | Partial | same | Same business function thrice | P0 |

**Module 6 exit criteria:** Learner avoids UDF when native exists and interprets plan opacity.

---

## Cross-cutting & repo mechanics (not a “module” but required)

| ID | Item | Current | Action |
|----|------|---------|--------|
| X.1 | Renumber/rename directories `01`…`06` to match new story | Misaligned | Decide: rename folders vs keep paths + README map |
| X.2 | `scripts/generate_notebooks.py` sync with notebooks | Drift risk | Regenerate or stop using generator for edited modules |
| X.3 | Root `README.md` module table | Old titles | Update after renumber |
| X.4 | Shared data (`config.WORKSHOP_MONTHS`) sized for long workshop | Small | May need more months / module-specific subsets |
| X.5 | `begin_module()` + TLC download in cell 1 | Full | Keep for all modules |
| X.6 | Drop or relocate **Module 06 Java GC** | Exists | Product decision |

---

## Traceability: request sentence → matrix IDs

| User request (paraphrased) | Matrix IDs |
|--------------------------|------------|
| M1 PySpark & SparkSQL parity, same processing | 1.1–1.2 |
| M1 logical → analyzer → optimizer → physical | 1.3–1.6 |
| M2 column selection, filter pushdown | 2.1–2.2 |
| M2 all join strategies + equi/inequi + two equi fix | 2.4–2.12 |
| M3 JSON/CSV/Parquet/Iceberg RW + benchmarks | 3.1–3.5 |
| M3 type safety read/write + explicit schema | 3.6–3.7 |
| M3 DSv2, metadata, manifests, snapshots, compaction | 3.8–3.14 |
| M4 actions/jobs; observation; cache/checkpoint; intermediate table | 4.1–4.11 |
| M5 locality/shuffle; hints; query reshape; SPJ cases | 5.1–5.13 |
| M6 UDF slowness, planner, serde, Pandas, native | 6.1–6.8 |

---

## Implementation checklist (fill in as you edit)

| Module | Rows P0 | P0 Done | Notebook PR/commit |
|--------|-----------|---------|---------------------|
| 1 | 6 | 6 | `01_spark_plans.ipynb` v1 |
| 2 | 11 | 9 | `02_plan_joins.ipynb` v1 (BLNJ label optional) |
| 3 | 10 | 10 | `03_storage_io.ipynb` v1 + `CALL local.system.rewrite_data_files` |
| 4 | 8 | 8 | `04_lazy_execution.ipynb` v1 |
| 5 | 9 | 8 | `05_data_locality.ipynb` v1 (compatible-transform SPJ P1) |
| 6 | 6 | 6 | `06_udfs.ipynb` v1 |

---

## Open decisions (answer before large rewrites)

1. **Folder renumbering:** e.g. `02_plan_joins`, `04_lazy_execution`, `05_locality_spj` — yes/no? yes
2. **Module 2 placement:** new notebook vs split across 01+05? remove existing modules, add new ones split per topic
3. **Synthetic data** for `user_id` / `post_id` shuffle lesson (5.5) vs TLC-only? synthetic data is ok to demonstrate the point
4. **Iceberg compaction API** version locked to Spark 4.1 + Iceberg 1.12 — confirm procedure names. leave this open for now
5. **Inequi “two equi joins”** — canonical pattern (band join decomposition) to avoid misleading results? sure

When these are decided, update this file’s **Target notebook** column and proceed module-by-module in P0 order.