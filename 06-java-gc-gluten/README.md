# Module 06 — Java GC & Gluten

**Duration:** ~60 minutes

## Learning Objectives

- Understand driver vs executor JVM memory
- Read GC metrics from Spark UI Executors tab
- Know common GC tuning strategies (G1, ZGC)
- Understand Gluten native acceleration (optional demo)

## Part A — JVM / GC (All Attendees)

Monitor these in Spark UI → **Executors** → **GC Time**:

| Config | Purpose |
|--------|---------|
| `spark.driver.memory` | Driver heap |
| `spark.executor.memory` | Executor heap |
| `spark.memory.fraction` | Spark vs user memory split |
| `spark.executor.extraJavaOptions` | GC flags |

### GC Strategies (Java 17+)

| GC | Flag | Use case |
|----|------|----------|
| G1 (default) | `-XX:+UseG1GC` | General purpose |
| ZGC | `-XX:+UseZGC` | Low-latency, large heaps |

Edit `docker/spark-defaults.conf` and restart the cluster to experiment.

## Part B — Gluten (Optional)

Gluten offloads Spark SQL to native engines (Velox). **Gluten 1.7.0** has official Spark 4.1 binaries but excludes Iceberg in preview builds.

### Setup

1. Download Gluten 1.7.0 Spark 4.1 binary from [gluten.apache.org/downloads](https://gluten.apache.org/downloads/)
2. Extract JARs and native libraries into the `gluten-jars` Docker volume
3. Start with Gluten profile:

```bash
make up-gluten
```

4. Open `06_java_gc_gluten_template.ipynb` — Part B detects `SPARK_GLUTEN_ENABLED`

The Gluten demo uses plain Parquet (not Iceberg) for the benchmark.

## Files

| File | Purpose |
|------|---------|
| `06_java_gc_gluten_template.ipynb` | Instructor walkthrough |
| `exercises/06_exercise.ipynb` | Attendee exercise |

## Exercise

Run a memory-heavy aggregation, record GC Time from the UI, and write three tuning recommendations.
