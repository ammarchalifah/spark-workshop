# Module 03 — Storage I/O Performance

**Duration:** ~60 minutes

## Learning Objectives

- Compare read performance: JSON, Parquet (serial vs vectorized), Iceberg
- Compare write performance: JSON, CSV, Parquet, Iceberg
- Understand columnar vs row-based storage trade-offs
- Observe Iceberg metadata pruning and filter pushdown

## Benchmark Matrix

### Reads

| Format | Config | Expected |
|--------|--------|----------|
| JSON | default | Slowest |
| Parquet | `enableVectorizedReader=false` | Serial, slower |
| Parquet | vectorized (default) | Fast |
| Iceberg | snapshot read | Fast + metadata pruning |

### Writes

| Format | Notes |
|--------|-------|
| JSON | Row-based, large files |
| CSV | No schema, parsing overhead |
| Parquet | Columnar, efficient |
| Iceberg | Parquet + snapshot metadata |

All outputs go to `data/output/03-*` (gitignored).

## Files

| File | Purpose |
|------|---------|
| `03_storage_io_template.ipynb` | Instructor walkthrough |
| `exercises/03_exercise.ipynb` | Attendee exercise |

## Exercise

Write 200k rows to Parquet and Iceberg. Time filtered vs unfiltered reads. Explain why Iceberg reads fewer files with a filter.
