# Module 02 — Lazy Execution

**Duration:** ~60 minutes

## Learning Objectives

- Distinguish transformations (lazy) from actions (eager)
- Understand how an action triggers the entire DAG
- Recognize branching DAGs that cause duplicated work
- Apply mitigations: cache, checkpoint, and Spark Observation

## Concepts

| Term | Behavior |
|------|----------|
| Transformation | Lazy — builds DAG, no execution |
| Action | Eager — triggers Spark job(s) |
| Lineage | DAG of transformations back to source |
| Cache | In-memory/disk shortcut for reuse within session |
| Checkpoint | Breaks lineage by writing to reliable storage |

## Spark UI Checkpoints

For each demo, watch the **Jobs** tab:

1. After building transformations only — no new jobs
2. After first `.count()` — one job appears
3. After branched actions without cache — duplicated scan stages
4. After `.cache()` — second action reuses cached data

## Files

| File | Purpose |
|------|---------|
| `02_lazy_execution_template.ipynb` | Instructor walkthrough |
| `exercises/02_exercise.ipynb` | Attendee exercise |

## Exercise

Refactor a three-action pipeline to eliminate duplicate scans. Compare job count before and after in the Spark UI.
