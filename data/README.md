# Workshop Data

## Input Data (Public, Runtime Fetch)

Workshop datasets come from public NYC TLC URLs but are **downloaded to `data/cache/`** before Spark reads them. Spark cannot read Parquet directly from HTTPS. No large files are committed to this repository.

| Dataset | URL | Used in |
|---------|-----|---------|
| Yellow taxi (Jan–Feb 2024) | `.../yellow_tripdata_2024-0{1,2}.parquet` | Modules 01–02, 04–06 |
| Yellow taxi (Jan–Jun 2024) | `.../yellow_tripdata_2024-0{1..6}.parquet` | Module 03 I/O benchmarks |
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

## Docker Mount

In Docker mode, the host `data/` directory is bind-mounted at `/workspace/data` across master, workers, and Jupyter. Files cached with `make cache-data` on the host are immediately visible inside containers.
