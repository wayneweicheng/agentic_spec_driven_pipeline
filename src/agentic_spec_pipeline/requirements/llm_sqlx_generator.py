from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import json
import re

from .llm_preprocessor import _call_llm_with_adk, _call_llm_with_genai

SYSTEM = (
    "You are a senior data engineer generating BigQuery SQLX (Dataform) code. "
    "Given a structured spec JSON (models, schemas, mappings, joins, filters, aggregations, constraints), "
    "emit robust SQL for each model using multiple CTEs when appropriate. "
    "Handle complex patterns such as SCD2 MERGE, windowed metrics, JSON extraction, array unnest, pivots, and dedup with window functions as needed. "
    "Target BigQuery dialect; do not include explanations—output only the SQL code per model."
)

INSTRUCTIONS = (
    "Instructions:\n"
    "- For each model, generate a complete SQLX body (config header and SQL).\n"
    "- Use config { type: \"table\", schema: \"<schema>\" } based on layer (staging->staging_schema, final->final_schema).\n"
    "- Use WITH CTEs for mappings/joins/filters.\n"
    "- If constraints indicate SCD2, produce MERGE pattern with effective/expiry timestamps.\n"
    "- If aggregations present, create appropriate GROUP BY or window logic.\n"
    "- Output as JSON mapping model_name -> sqlx_text (string). Return ONLY JSON, no code fences."
)

PER_MODEL_INSTRUCTIONS = (
    "Instructions:\n"
    "- Generate a complete SQLX body (config header and SQL) for this model only.\n"
    "- Use config { type: \"table\", schema: \"<schema>\" } based on layer (staging->staging_schema, final->final_schema).\n"
    "- Use WITH CTEs for mappings/joins/filters.\n"
    "- If constraints indicate SCD2, produce MERGE with effective/expiry timestamps.\n"
    "- Output JSON: {\"sqlx_text\": string | {\"config\": string, \"sql\": string}}. Return ONLY JSON."
)


def _call_llm_general(spec: Dict[str, Any], model_name: str) -> str:
    spec_min = json.dumps(spec, separators=(",", ":"))
    prompt = (
        SYSTEM
        + "\n\nSpec JSON (minimized):\n"
        + spec_min
        + "\n\n"
        + INSTRUCTIONS
    )
    try:
        return _call_llm_with_adk(prompt, model_name)
    except Exception:
        return _call_llm_with_genai(prompt, model_name)


def _call_llm_per_model(spec: Dict[str, Any], model: Dict[str, Any], model_name: str) -> str:
    payload = {"schema": spec.get("schema", {}), "model": model}
    payload_min = json.dumps(payload, separators=(",", ":"))
    prompt = (
        SYSTEM
        + "\n\nSpec/Model JSON (minimized):\n"
        + payload_min
        + "\n\n"
        + PER_MODEL_INSTRUCTIONS
    )
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


def _schema_for_layer(spec_schema: Dict[str, Any], layer: str) -> str:
    if layer == "staging":
        return spec_schema.get("staging_schema", "staging")
    return spec_schema.get("final_schema", "analytics")


def _normalize_sqlx_value(value: Any, spec: Dict[str, Any], model: Dict[str, Any]) -> str:
    if isinstance(value, str):
        v = value.strip()
        if v.startswith("{") and v.endswith("}"):
            try:
                obj = json.loads(v)
                return _normalize_sqlx_value(obj, spec, model)
            except Exception:
                return value
        return value
    if isinstance(value, dict):
        config_text = value.get("config")
        sql_text = value.get("sql")
        if isinstance(config_text, dict):
            layer_schema = _schema_for_layer(spec.get("schema", {}), model.get("layer", "final"))
            config_line = f"config {{ type: \"table\", schema: \"{layer_schema}\" }}"
        elif isinstance(config_text, str) and config_text.strip():
            config_line = config_text.strip()
        else:
            layer_schema = _schema_for_layer(spec.get("schema", {}), model.get("layer", "final"))
            config_line = f"config {{ type: \"table\", schema: \"{layer_schema}\" }}"
        sql_body = sql_text if isinstance(sql_text, str) else ""
        composed = f"{config_line}\n{sql_body}\n"
        return composed
    return str(value)


def generate_sqlx_with_llm(spec: Dict[str, Any], out_dir: Path, model_name: str) -> List[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    text = _call_llm_general(spec, model_name)
    written: List[str] = []
    try:
        data = _extract_json(text)
        if isinstance(data, dict):
            spec_names = {m.get("name") for m in spec.get("models", []) if m.get("name")}
            candidate = data.get("models") if isinstance(data.get("models"), dict) else data
            filtered: Dict[str, Any] = {k: v for k, v in candidate.items() if k in spec_names}
            if filtered:
                for name, val in filtered.items():
                    model_meta = next((m for m in spec.get("models", []) if m.get("name") == name), {"name": name})
                    sqlx_text = _normalize_sqlx_value(val, spec, model_meta)
                    path = out_dir / f"{name}.sqlx"
                    if not sqlx_text.endswith("\n"):
                        sqlx_text = sqlx_text + "\n"
                    path.write_text(sqlx_text)
                    written.append(str(path))
                if written:
                    return written
    except Exception:
        pass

    # Fallback: per-model generation
    for model in spec.get("models", []):
        resp = _call_llm_per_model(spec, model, model_name)
        obj = _extract_json(resp)
        name = model.get("name", "model")
        raw_val = obj.get("sqlx_text", obj)
        sqlx_text = _normalize_sqlx_value(raw_val, spec, model)
        path = out_dir / f"{name}.sqlx"
        if not sqlx_text.endswith("\n"):
            sqlx_text = sqlx_text + "\n"
        path.write_text(sqlx_text)
        written.append(str(path))
    return written
