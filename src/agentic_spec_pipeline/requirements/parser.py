import re
from typing import Any, Dict
import yaml
from .table_parser import parse_models_from_markdown

FENCED_YAML = re.compile(r"```yaml\s*([\s\S]*?)\s*```", re.IGNORECASE)
# Only match frontmatter at the very start of the document
FRONTMATTER_START = re.compile(r"\A---\s*\n([\s\S]*?)\n---\s*", re.MULTILINE)


def parse_requirements_markdown(markdown_text: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}

    match = FENCED_YAML.search(markdown_text)
    if not match:
        match = FRONTMATTER_START.match(markdown_text)
    if match:
        yaml_text = match.group(1)
        data = yaml.safe_load(yaml_text) or {}

    # Defaults
    data.setdefault("schema", {})
    data["schema"].setdefault("raw_schema", "raw")
    data["schema"].setdefault("staging_schema", "temp")
    data["schema"].setdefault("final_schema", "analytics")

    # Table-driven models
    models = parse_models_from_markdown(markdown_text)
    if models:
        # Convert to a serializable list for downstream generators that expect dicts
        data["models"] = [
            {
                "name": m.name,
                "layer": m.layer,
                "sources": m.sources,
                "column_mapping": m.column_mapping,
                "joins": m.joins,
                "filters": m.filters,
                "aggregations": m.aggregations,
                "group_by": m.group_by,
                "constraints": m.constraints,
            }
            for m in models
        ]

    data.setdefault("sources", [])
    data.setdefault("mocks", {})

    return data
