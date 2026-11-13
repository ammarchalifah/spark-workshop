# Module 01 — How Spark Works

## Learning Objectives

- Understand distributed computing in Spark: driver, executors, partitions, tasks
- Read the Spark UI: differentiate **Jobs**, **Stages**, and **Tasks**
- See how shuffle creates **stage boundaries** (without diving into join strategies)
- Understand that physical plans change based on **configuration**

## Concepts

| Term | Definition |
|------|------------|
| **Job** | Triggered by an **action** (e.g. `.count()`). |
| **Stage** | Pipeline of tasks separated by a shuffle (data moving across the cluster). |
| **Task** | Unit of work on a single partition, run on one executor core. |
| **Transformation** | Lazy — builds the DAG. |
| **Action** | Triggers execution. |

## Demo Flow

1. **Aggregation** — observe jobs, stages, tasks
2. **Window function** — shuffle creates a new stage boundary
3. **Combining two datasets** — more stages appear (don't focus on *how* yet)
4. **Config changes** — alter `spark.sql.shuffle.partitions`, compare plans and task counts
5. **Live discussion** — walk through UI together

## Spark UI

- **Master UI:** http://localhost:8080
- **Application UI:** http://localhost:4040

## Notebook

`01_how_spark_works.ipynb` — instructor-led walkthrough with live discussion prompts at the end.
