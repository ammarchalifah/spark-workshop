# Module 04 — UDF Performance

**Duration:** ~60 minutes

## Learning Objectives

- Understand JVM ↔ Python serialization cost
- Benchmark vanilla Python UDF vs Pandas UDF vs native Spark
- Know when each approach is appropriate

## Approaches

| Type | Mechanism | Performance |
|------|-----------|-------------|
| Python UDF | Row-by-row pickle serialization | Slowest |
| Pandas UDF | Arrow batch transfer | Medium |
| Native Spark | JVM-only execution | Fastest |

## Spark UI Checkpoints

Look for `PythonUDF` in the physical plan and Stages tab when running Python UDFs. Native functions show no Python boundary.

## Files

| File | Purpose |
|------|---------|
| `04_udfs_template.ipynb` | Instructor walkthrough |
| `exercises/04_exercise.ipynb` | Attendee exercise |

## Exercise

Rewrite a provided Python UDF as a Pandas UDF and as native Spark SQL. Report speedup ratios.
