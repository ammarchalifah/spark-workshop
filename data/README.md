# Data layout

## Input (cache)

Datasets come from NYC TLC HTTPS URLs. Spark does not read Parquet over HTTPS, so the Jupyter kernel downloads files into `data/cache/` via `shared.config.ensure_workshop_data()` (called from `begin_module()` in the first cell of each module).

| File | Source |
|------|--------|
| `yellow_tripdata_2024-01.parquet` | TLC trip data |
| `yellow_tripdata_2024-02.parquet` | TLC trip data |
| `taxi_zone_lookup.csv` | TLC zone lookup |

First module start may take a few minutes while ~100 MB downloads. Later runs skip files that already exist.

## Output (gitignored)

| Path | Contents |
|------|----------|
| `data/output/warehouse/` | Iceberg tables (Hadoop catalog) |
| `data/output/checkpoints/` | RDD/DataFrame checkpoints |
| `data/output/spark-events/` | Event logs (if enabled) |

## Bind mount

`./data` on the host maps to `/workspace/data` in master, workers, and Jupyter. Downloads and warehouse files persist across container restarts.
