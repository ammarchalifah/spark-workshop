# Module 05 — Shuffle & Sort

**Duration:** ~60 minutes

## Learning Objectives

- Compare join strategies: broadcast, shuffle hash, sort-merge
- Configure and verify Storage Partitioned Join (SPJ) with Iceberg
- Understand table-level ordering and its effect on write/read performance

## Join Strategies

| Strategy | When | UI Signature |
|----------|------|-------------|
| Broadcast | Small table fits threshold | `BroadcastExchange` |
| Shuffle Hash | Medium tables, no sort | `Exchange hashpartitioning` |
| Sort-Merge | Large tables (default) | `Sort` + `Exchange` |

## SPJ Configuration

```
spark.sql.sources.v2.bucketing.enabled=true
spark.sql.sources.v2.bucketing.pushPartValues.enabled=true
spark.sql.iceberg.planning.preserve-data-grouping=true
spark.sql.requireAllClusterKeysForCoPartition=false
```

Both Iceberg tables must share compatible partitioning. Join keys must include partition columns.

## Table Ordering

`ALTER TABLE ... WRITE ORDERED BY (...)` sets `write.distribution-mode=range`, causing a global sort on write. Pre-sorted input with `use-table-distribution-and-ordering=false` can avoid redundant shuffles.

## Files

| File | Purpose |
|------|---------|
| `05_shuffle_sort_template.ipynb` | Instructor walkthrough |
| `exercises/05_exercise.ipynb` | Attendee exercise |

## Exercise

Create two partitioned Iceberg tables. Compare physical plans with SPJ enabled vs disabled.
