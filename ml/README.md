# ML Research & Evaluation Workspace (`ml/`)

This directory houses offline machine learning experimentation, retrieval benchmarks, and synthetic/curated dataset utilities for **VeriMed**.

## Architectural Boundary
- **Strict Isolation**: Production API code in `apps/api/` must **never** import modules from `ml/`.
- Artifacts, evaluation scripts, and model comparison configurations live here so data science experimentation remains decoupled from production inference services.
