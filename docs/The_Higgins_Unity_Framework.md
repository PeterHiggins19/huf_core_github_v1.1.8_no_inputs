# The Higgins Unity Framework (HUF)

This project is the **HUF Core** implementation: a practical toolkit you can run to turn messy real‑world datasets into *consistent, comparable* outputs.

If you’re not technical, don’t worry — you can still use HUF by following the step‑by‑step guides.

## Plain‑English idea

Real systems produce lots of different signals:

- budgets, traffic timing, anomalies, logs, counts, categories…
- all with different units, scales, and missing values

**HUF’s core trick** is to convert those signals into a *normalized representation* so that:

- different sources can be compared fairly
- changes over time are easier to detect
- “what matters most” can be ranked without hand‑tuning every dataset

In this repo, that “normalization” mostly shows up as:

- cleaning inputs
- mapping columns into a consistent schema
- producing standardized outputs you can analyze or visualize

## What you get from this repository

- **Repeatable demos (“cases”)** with real civic datasets (Markham + Toronto)
- A **command line tool** (`huf ...`) to run those cases
- A structure you can copy to add **your own data adapters and cases**

## Key concepts (no math)

### 1) Inputs → adapters → outputs
A “case” takes some input file(s), runs a transformation, and writes results to an output folder.

- Input examples: `.xlsx`, `.csv`, large datasets (Planck is guided/manual)
- Output examples: cleaned tables, normalized metrics, reports

### 2) Normalization (the “unity” idea)
Normalization means turning different kinds of numbers into a consistent scale so they can be compared.

Example:
- Dataset A ranges from 0–10
- Dataset B ranges from 0–10,000

After normalization, both can live on the same scale, so ranking and anomaly detection are meaningful.

### 3) “Cases” are learning modules
Each case is both:
- a working example you can run today
- a template you can copy when adding your own workflow

## Where to begin

1. **Follow the beginner path:** [Learning Path](learning_path.md)  
2. **Run a demo:** [Cases](cases.md)  
3. **If you hit errors:** [Troubleshooting](troubleshooting.md)

## Advanced / theory (optional)

Some HUF writings discuss deeper mathematics (categories, morphisms, topology, etc.).
Those are **not required** to run the tools in this repo.

If you want the deeper background, start with:
- [Theory Notes](theory_notes.md)
- [Handbook](handbook.md)

## Glossary

- **Case**: a runnable example workflow (input → process → output).
- **Adapter**: code that reads a particular dataset shape and maps it into HUF’s expected schema.
- **Normalization**: converting values into a consistent scale to compare across sources.
- **Schema**: the column names / fields that HUF expects for a given workflow.

---

*Note:* The original author notes and drafts existed as `.Markdown`. This repo now keeps documentation in Markdown (`.md`) so it renders well on GitHub and GitHub Pages.
