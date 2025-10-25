# Agentic Spec-Driven Pipeline

This repository contains a specification-driven agent built on Google ADK that:
- Converts narrative/table-driven Markdown requirements into normalized JSON specifications and mapping docs
- Generates data pipeline code (Dataform SQLX, DBT, Spark, etc.) from specifications
- Automatically generates comprehensive tests from specifications

The methodology is platform-agnostic and can be adapted for various data pipeline tools.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e .
# optional: LLM fallback client
pip install -e '.[llm]'
export GOOGLE_API_KEY=YOUR_KEY   # if using LLM (AI Studio)
```

## Canonical Flow

1) Requirements → Spec + Mapping Docs
```bash
python -m agentic_spec_pipeline spec-from-req \
  --req examples/requirements/customer_order_pipeline_requirement.md \
  --out-root examples/generated_project \
  --use-llm   # optional; uses ADK or google-generativeai
```
Outputs:
- `examples/generated_project/spec.json`
- `examples/generated_project/mappings/*.md`

2) Spec → Pipeline Code
```bash
python -m agentic_spec_pipeline sqlx-from-spec \
  --spec examples/generated_project/spec.json \
  --out-dir examples/generated_project/definitions
```

3) Spec → Tests
```bash
python -m agentic_spec_pipeline tests-from-spec \
  --spec examples/generated_project/spec.json \
  --out-dir tests/generated
```

## Notes
- `ADK_DEFAULT_MODEL` in your environment controls the default LLM (e.g., `gemini-2.5-flash`).
- LLM is optional; you can parse deterministically without `--use-llm`.
- Spec and mapping docs are the source of truth for code/test generation.