from pathlib import Path
from typing import Any, Dict, List
from .sql_builder import build_sqlx_from_model


def _to_ref(name: str) -> str:
    return f"${{ref('{name}')}}"


def _emit_config(schema: str) -> str:
    return (
        "config {\n"
        f"  type: \"table\",\n  schema: \"{schema}\"\n"
        "}\n\n"
    )


def _generate_model_sqlx(model: Dict[str, Any], schema_map: Dict[str, str]) -> str:
    # If table-driven fields are present, delegate to builder
    if model.get("column_mapping") or model.get("aggregations"):
        from .table_parser import ModelSpec

        spec = ModelSpec(
            name=model["name"],
            layer=model.get("layer", "staging"),
            sources=model.get("sources", []),
            column_mapping=model.get("column_mapping", []),
            joins=model.get("joins", []),
            filters=model.get("filters", []),
            aggregations=model.get("aggregations", []),
            group_by=model.get("group_by", []),
            constraints=model.get("constraints", {}),
        )
        return build_sqlx_from_model(spec, schema_map["staging_schema"], schema_map["final_schema"])

    layer = model.get("layer", "staging")
    schema = schema_map["staging_schema"] if layer == "staging" else schema_map["final_schema"]

    parts: List[str] = []
    parts.append(_emit_config(schema))

    ctes = model.get("ctes", [])
    if ctes:
        cte_sqls: List[str] = []
        for c in ctes:
            cte_sqls.append(f"{c['name']} AS (\n{c['select'].strip()}\n)\n")
        with_block = "WITH\n" + ",\n\n".join(cte_sqls) + "\n"
        parts.append(with_block)

    final_select = model.get("final_select", "SELECT 1 AS placeholder")
    parts.append(final_select + "\n")

    return "\n".join(parts)


def generate_sqlx_from_requirements(req: Dict[str, Any], out_dir: Path) -> Path:
    schema_map = req["schema"]
    models = req.get("models", [])

    out_dir.mkdir(parents=True, exist_ok=True)

    last_path: Path | None = None
    for model in models:
        name = model["name"]
        sqlx_text = _generate_model_sqlx(model, schema_map)
        path = out_dir / f"{name}.sqlx"
        path.write_text(sqlx_text)
        last_path = path

    # Backward compatibility for single transform spec (if present)
    if not models and req.get("transforms"):
        final_name = req.get("final", {}).get("name", "final_output")
        parts: List[str] = []
        parts.append(_emit_config(schema_map["final_schema"]))
        transform_sqls: List[str] = []
        for t in req.get("transforms", []):
            transform_sqls.append(f"{t['name']} AS (\n{t['select'].strip()}\n)\n")
        if transform_sqls:
            with_block = "WITH\n" + ",\n\n".join(transform_sqls) + "\n"
            parts.append(with_block)
        final_select = req.get("final", {}).get("select", "SELECT 1 AS placeholder")
        parts.append(final_select + "\n")
        text = "\n".join(parts)
        path = out_dir / f"{final_name}.sqlx"
        path.write_text(text)
        last_path = path

    return last_path or (out_dir / "_no_models.sqlx")
