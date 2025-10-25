from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import json


def _md_table(headers: List[str], rows: List[List[Any]]) -> str:
    header_row = "| " + " | ".join(headers) + " |"
    sep_row = "|" + "|".join(["-" * (len(h) + 2) for h in headers]) + "|"
    data_rows = []
    for r in rows:
        cells = [("" if (c is None) else str(c)) for c in r]
        data_rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([header_row, sep_row, *data_rows])


def _write_model_doc(model: Dict[str, Any], out_dir: Path) -> Path:
    name = model.get("name", "model")
    out_dir.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []

    layer = model.get("layer", "staging")
    sources = ", ".join(model.get("sources", []))
    lines.append(f"# Model: {name} (layer: {layer})\n")
    if sources:
        lines.append(f"Sources: {sources}\n")

    # Column mapping
    cols = model.get("column_mapping", [])
    if cols:
        lines.append("## Column mapping\n")
        headers = [
            "target_column",
            "type",
            "from_table",
            "from_column",
            "transform",
            "nullable",
            "tests",
            "description",
        ]
        rows = []
        for c in cols:
            tests_val = c.get("tests", "")
            if isinstance(tests_val, list):
                tests_val = ",".join(str(t) for t in tests_val)
            rows.append([
                c.get("target_column", ""),
                c.get("type", ""),
                c.get("from_table", ""),
                c.get("from_column", ""),
                c.get("transform", ""),
                c.get("nullable", ""),
                tests_val,
                c.get("description", ""),
            ])
        lines.append(_md_table(headers, rows) + "\n")

    # Joins
    joins = model.get("joins", [])
    if joins:
        lines.append("## Joins\n")
        headers = ["left_table", "right_table", "type", "condition"]
        rows = [
            [
                j.get("left_table", ""),
                j.get("right_table", ""),
                j.get("type", ""),
                j.get("condition", ""),
            ]
            for j in joins
        ]
        lines.append(_md_table(headers, rows) + "\n")

    # Filters
    filters = model.get("filters", [])
    if filters:
        lines.append("## Filters\n")
        headers = ["applies_to", "predicate", "rationale"]
        rows = [
            [
                f.get("applies_to", ""),
                f.get("predicate", ""),
                f.get("rationale", ""),
            ]
            for f in filters
        ]
        lines.append(_md_table(headers, rows) + "\n")

    # Aggregations
    aggs = model.get("aggregations", [])
    if aggs:
        lines.append("## Aggregations\n")
        headers = ["metric_column", "type", "formula", "tests", "description"]
        rows = []
        for a in aggs:
            tests_val = a.get("tests", "")
            if isinstance(tests_val, list):
                tests_val = ",".join(str(t) for t in tests_val)
            rows.append([
                a.get("metric_column", ""),
                a.get("type", ""),
                a.get("formula", ""),
                tests_val,
                a.get("description", ""),
            ])
        lines.append(_md_table(headers, rows) + "\n")

    # Group by
    group_by = model.get("group_by", [])
    if group_by:
        lines.append("## Group by\n")
        headers = ["group_key"]
        rows = [[k] for k in group_by]
        lines.append(_md_table(headers, rows) + "\n")

    # Constraints
    constraints = model.get("constraints", {})
    if constraints:
        lines.append("## Output constraints\n")
        headers = list(constraints.keys())
        rows = [list(constraints.values())]
        lines.append(_md_table(headers, rows) + "\n")

    out_path = out_dir / f"{name}.md"
    out_path.write_text("\n".join(lines))
    return out_path


def write_spec_artifacts(spec: Dict[str, Any], definitions_dir: Path) -> Dict[str, Any]:
    """
    Write a machine-readable spec.json and per-model mapping docs next to the generated project.
    - spec.json at <project_root>/spec.json
    - mappings/<model>.md per model
    Returns a summary with written paths.
    """
    project_root = definitions_dir.parent
    project_root.mkdir(parents=True, exist_ok=True)

    # Write JSON spec
    spec_path = project_root / "spec.json"
    spec_path.write_text(json.dumps(spec, indent=2))

    # Write per-model mapping docs
    mappings_dir = project_root / "mappings"
    written_md: List[str] = []
    for model in spec.get("models", []):
        p = _write_model_doc(model, mappings_dir)
        written_md.append(str(p))

    return {"spec_json": str(spec_path), "mapping_docs": written_md}
