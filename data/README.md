# Data layout

## Input (cache)

Datasets come from NYC TLC HTTPS URLs. Spark does not read Parquet over HTTPS, so files are stored under `data/cache/` before notebooks use them. Nothing large is committed to git.

| File | Source |
|------|--------|
| `yellow_tripdata_2024-01.parquet` | TLC trip data |
| `yellow_tripdata_2024-02.parquet` | TLC trip data |
| `taxi_zone_lookup.csv` | TLC zone lookup |

Pre-download (optional):

```bash
./scripts/cache-data.sh
```

```powershell
.\scripts\cache-data.ps1
```

Notebooks can also download missing files on first access via `shared.config.ensure_workshop_data()`.

## Output (gitignored)

| Path | Contents |
|------|----------|
| `data/output/warehouse/` | Iceberg tables (Hadoop catalog) |
| `data/output/checkpoints/` | RDD/DataFrame checkpoints |
| `data/output/spark-events/` | Event logs (if enabled) |

## Bind mount

`./data` on the host maps to `/workspace/data` in master, workers, and Jupyter. Host-side cache scripts and in-container reads see the same files.
