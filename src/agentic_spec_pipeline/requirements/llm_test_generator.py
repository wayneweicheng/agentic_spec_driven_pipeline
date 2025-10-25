from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import json
import re

from .llm_preprocessor import _call_llm_with_adk, _call_llm_with_genai

SYSTEM = (
    "You are a senior data engineer generating rigorous BigQuery SQL test scripts. "
    "Given a structured spec JSON (models, schemas, mappings, joins, filters, aggregations, constraints), "
    "emit a set of SQL files that validate transformations, including edge cases and invariants. "
    "Produce inline temp tables for fixtures as needed. For complex logic (SCD2, windowing), assert key invariants."
)

INSTRUCTIONS = (
    "Instructions:\n"
    "- Generate a mapping of model_name -> test_sql (single file per model).\n"
    "- In each SQL, create temp tables for required fixtures and assertions.\n"
    "- Focus assertions on primary keys, dedup, SCD2 validity periods, aggregates correctness, and nullability/accepted values.\n"
    "- Output JSON mapping model_name -> test_sql. Return ONLY JSON, no code fences."
)

PER_MODEL_INSTRUCTIONS = (
    "Instructions:\n"
    "- Generate one BigQuery SQL test for THIS model.\n"
    "- Include temp tables/CTEs for fixtures and assertions.\n"
    "- Focus on invariants relevant to the model's logic.\n"
    "- Output JSON: {\"test_sql\": string | {\"sql\": string, \"assertions\": [string]}}. Return ONLY JSON."
)


def _call_llm_general(spec: Dict[str, Any], model_name: str) -> str:
    spec_min = json.dumps(spec, separators=(",", ":"))
    prompt = SYSTEM + "\n\nSpec JSON (minimized):\n" + spec_min + "\n\n" + INSTRUCTIONS
    try:
        return _call_llm_with_adk(prompt, model_name)
    except Exception:
        return _call_llm_with_genai(prompt, model_name)


def _call_llm_per_model(spec: Dict[str, Any], model: Dict[str, Any], model_name: str) -> str:
    payload = {"schema": spec.get("schema", {}), "model": model}
    payload_min = json.dumps(payload, separators=(",", ":"))
    prompt = SYSTEM + "\n\nSpec/Model JSON (minimized):\n" + payload_min + "\n\n" + PER_MODEL_INSTRUCTIONS
    try:
        return _call_llm_with_adk(prompt, model_name)
    except Exception:
        return _call_llm_with_genai(prompt, model_name)


_JSON_RE = re.compile(r"\{[\s\S]*\}")


def _extract_json(text: str) -> Dict[str, Any]:
    s = text.strip()
    if s.startswith("```"):
        parts = s.split("```", 2)
        if len(parts) == 3:
            body = parts[1]
            if body.startswith("json"):
                body = body[4:]
            s = body
    m = _JSON_RE.search(s)
    if not m:
        raise ValueError("LLM did not return JSON")
    return json.loads(m.group(0))


def _normalize_test_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        # Common shapes: {"sql": "..."} or {"test_sql": "..."} or {"queries": ["..."]}
        if isinstance(value.get("test_sql"), str):
            return value["test_sql"]
        if isinstance(value.get("sql"), str):
            return value["sql"]
        if isinstance(value.get("queries"), list):
            parts = [q for q in value["queries"] if isinstance(q, str) and q.strip()]
            return "\n;\n".join(parts)
        # Fallback stringify
        return json.dumps(value)
    return str(value)


def generate_tests_with_llm(spec: Dict[str, Any], out_dir: Path, model_name: str) -> List[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    text = _call_llm_general(spec, model_name)
    written: List[str] = []
    try:
        data = _extract_json(text)
        if isinstance(data, dict) and data:
            all_str = all(isinstance(v, (str, dict)) for v in data.values())
            if all_str:
                for name, val in data.items():
                    test_sql = _normalize_test_value(val)
                    path = out_dir / f"test_{name}.sql"
                    if not test_sql.endswith("\n"):
                        test_sql = test_sql + "\n"
                    path.write_text(test_sql)
                    written.append(str(path))
                if written:
                    return written
    except Exception:
        pass

    # Per-model fallback
    for model in spec.get("models", []):
        resp = _call_llm_per_model(spec, model, model_name)
        obj = _extract_json(resp)
        raw_val = obj.get("test_sql", obj)
        test_sql = _normalize_test_value(raw_val)
        name = model.get("name", "model")
        path = out_dir / f"test_{name}.sql"
        if not test_sql.endswith("\n"):
            test_sql = test_sql + "\n"
        path.write_text(test_sql)
        written.append(str(path))
    return written
