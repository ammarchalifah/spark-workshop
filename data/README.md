# Workshop Data

## Input Data (Public, Runtime Fetch)

Workshop notebooks read from public NYC TLC datasets over HTTPS. No large files are committed to this repository.

| Dataset | URL | Used in |
|---------|-----|---------|
| Yellow taxi (Jan 2024) | `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet` | Modules 01–05 |
| Yellow taxi (Feb 2024) | `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-02.parquet` | Modules 01–05 |
| Taxi zone lookup | `https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv` | Module 01 |

### Offline / Slow Network

Pre-download datasets to avoid repeated HTTP reads:

```bash
make cache-data
```

Cached files land in `data/cache/` and are mounted into containers at `/workspace/data/cache/`. Notebooks automatically prefer cached paths when available.

## Output Data (Local, Gitignored)

All workshop writes go to `data/output/`:

```
data/output/
├── warehouse/          # Iceberg catalog root
├── 03-read-bench/      # Module 03 format comparisons
├── 03-write-bench/
├── 05-spj/             # SPJ demo tables
└── checkpoints/        # Module 02 checkpoints
```

These directories are created at runtime and excluded from git via `.gitignore`.

## Docker Volume

In Docker mode, `data/` is mounted as a named volume (`workshop-data`) at `/workspace/data` across master, workers, and Jupyter containers. This ensures Iceberg tables and benchmarks are visible to all executors.
