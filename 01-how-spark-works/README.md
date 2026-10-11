# Module 01 — How Spark Works

**Duration:** ~60 minutes

## Learning Objectives

- Understand distributed computing in Spark: driver, executors, partitions, tasks
- Read the Spark UI: differentiate **Jobs**, **Stages**, and **Tasks**
- Run aggregation, window function, and join examples and correlate code with UI
- Understand that Spark physical plans are **not deterministic** — they depend on table stats, configs, and data size

## Concepts

| Term | Definition |
|------|------------|
| **Job** | Triggered by an **action** (e.g. `.count()`). One job per action. |
| **Stage** | A pipeline of tasks separated by a **shuffle boundary** (Exchange). |
| **Task** | Unit of work on a single partition, run on one executor core. |
| **Transformation** | Lazy operation that builds the DAG (filter, select, join). |
| **Action** | Triggers execution (count, collect, write). |

## Spark UI Checkpoints

Open these URLs while running the notebook:

- **Master UI:** http://localhost:8080
- **Application UI:** http://localhost:4040

For each demo, observe:

1. **Jobs tab** — how many jobs each action creates
2. **Stages tab** — shuffle read/write bytes, duration
3. **SQL tab** — physical plan and (with AQE) adaptive plan

## Files

| File | Purpose |
|------|---------|
| `01_how_spark_works_template.ipynb` | Instructor walkthrough |
| `exercises/01_exercise.ipynb` | Attendee exercise |

## Exercise

Given a join query, identify in the Spark UI:

1. Which stage corresponds to the shuffle
2. How many tasks run per stage
3. How the plan changes when you disable broadcast join

Expected: attendees can explain why a join creates an Exchange stage and how broadcast join eliminates it.
