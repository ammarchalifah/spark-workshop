# Module 02 — Lazy Execution

**Duration:** ~60 minutes

## Learning Objectives

- Distinguish transformations (lazy) from actions (eager)
- See how branching DAGs cause **duplicated work** on expensive pipelines
- Apply mitigations: cache, checkpoint, and Spark Observation

## Concepts

| Term | Behavior |
|------|----------|
| Transformation | Lazy — builds DAG, no execution |
| Action | Eager — triggers Spark job(s) |
| Cache | Reuse materialized data within session |
| Checkpoint | Break lineage by writing to storage |

## Demo Flow

Uses an **expensive pipeline** (filter → window → aggregate → sort) so duplicated work is visible in both wall-clock time and the Spark UI:

1. Lazy transformations — no jobs until action
2. Branching DAG — two actions, duplicated shuffle stages
3. Three actions — pain multiplies
4. Cache — materialize once, reuse
5. Checkpoint — break lineage
6. Observation — metrics in a single action
7. Live discussion

## Notebook

`02_lazy_execution.ipynb` — instructor-led walkthrough with timing comparisons.
