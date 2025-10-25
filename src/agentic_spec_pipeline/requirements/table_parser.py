from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import re

TABLE_BLOCK_RE = re.compile(r"```markdown\s*([\s\S]*?)\s*```", re.IGNORECASE)
HEADER_SEP_RE = re.compile(r"^\|\s*-", re.MULTILINE)


def _parse_markdown_table(md_text: str) -> List[Dict[str, str]]:
    lines = [ln.strip() for ln in md_text.strip().splitlines() if ln.strip()]
    if len(lines) < 2:
        return []
    headers = [h.strip() for h in lines[0].strip('|').split('|')]
    # second line should be separator; skip it
    data_rows = lines[2:]
    rows: List[Dict[str, str]] = []
    for row in data_rows:
        cols = [c.strip() for c in row.strip('|').split('|')]
        # pad/truncate to headers length
        if len(cols) < len(headers):
            cols += [""] * (len(headers) - len(cols))
        elif len(cols) > len(headers):
            cols = cols[: len(headers)]
        rows.append(dict(zip(headers, cols)))
    return rows


@dataclass
class ModelSpec:
    name: str
    layer: str
    sources: List[str] = field(default_factory=list)
    column_mapping: List[Dict[str, str]] = field(default_factory=list)
    joins: List[Dict[str, str]] = field(default_factory=list)
    filters: List[Dict[str, str]] = field(default_factory=list)
    aggregations: List[Dict[str, str]] = field(default_factory=list)
    group_by: List[str] = field(default_factory=list)
    constraints: Dict[str, str] = field(default_factory=dict)


def parse_models_from_markdown(doc_text: str) -> List[ModelSpec]:
    models: List[ModelSpec] = []

    # Find model headers like: "### Model: stg_customers (schema: temp)"
    model_iter = re.finditer(r"(?m)^###\s+Model:\s*([^\s]+)\s*\(schema:\s*([^\)]+)\)\s*$", doc_text)
    model_spans = [(m.start(), m.end(), m.group(1).strip(), m.group(2).strip()) for m in model_iter]

    # Append end sentinel
    model_spans.append((len(doc_text), len(doc_text), "__end__", ""))

    for i in range(len(model_spans) - 1):
        start, _, model_name, schema_name = model_spans[i]
        next_start, _, _, _ = model_spans[i + 1]
        block = doc_text[start:next_start]

        # Sources line
        m_src = re.search(r"Sources:\s*`([^`]+)`", block)
        sources = []
        if m_src:
            srcs = [s.strip() for s in m_src.group(1).split(',')]
            sources = [s.split('.')[-1] for s in srcs]  # table names only

        # Determine layer from schema name
        layer = "staging" if schema_name == "temp" else "final"

        # Extract fenced tables by section titles
        def section_table(title: str) -> List[Dict[str, str]]:
            m = re.search(rf"{re.escape(title)}\n```markdown\n([\s\S]*?)\n```", block, re.IGNORECASE)
            if not m:
                return []
            return _parse_markdown_table(m.group(1))

        column_mapping = section_table("Column mapping")
        joins = section_table("Joins")
        filters = section_table("Filters")
        aggregations = section_table("Aggregations")
        group_by_rows = section_table("Group by")
        group_by = [r.get("group_key", "").strip() for r in group_by_rows if r.get("group_key")]
        constraints_rows = section_table("Output constraints")
        constraints = {}
        for r in constraints_rows:
            constraints.update({k.strip(): v.strip() for k, v in r.items() if k and v})

        models.append(
            ModelSpec(
                name=model_name,
                layer=layer,
                sources=sources,
                column_mapping=column_mapping,
                joins=joins,
                filters=filters,
                aggregations=aggregations,
                group_by=group_by,
                constraints=constraints,
            )
        )

    return [m for m in models if m.name != "__end__"]
