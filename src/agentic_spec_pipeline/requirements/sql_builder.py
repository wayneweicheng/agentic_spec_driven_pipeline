from __future__ import annotations
from typing import List
from .table_parser import ModelSpec


def _select_expr(col: dict) -> str:
    src = col.get("from_table", "").strip()
    src_col = col.get("from_column", "").strip()
    transform = (col.get("transform") or "").strip()
    target = col.get("target_column", "").strip()

    base = f"{src}.{src_col}" if src and src_col else "NULL"
    if "{from}" in transform:
        expr = transform.replace("{from}", base)
    elif transform:
        expr = transform
    else:
        expr = base
    return f"{expr} AS {target}"


def _build_staging_sql(model: ModelSpec) -> str:
    # Build FROM + JOINS
    sources = [s for s in model.sources]
    if not sources:
        return "SELECT 1 AS placeholder"  # safety

    from_table = sources[0]
    join_sqls: List[str] = []
    for j in model.joins:
        jt = j.get("type", "LEFT").upper()
        right = j.get("right_table", "").strip()
        cond = j.get("condition", "").strip()
        if right and cond:
            join_sqls.append(f"{jt} JOIN ${{ref('{right}')}} ON {cond}")

    where_sqls: List[str] = []
    for f in model.filters:
        pred = f.get("predicate", "").strip()
        applies_to = f.get("applies_to", "")
        if pred and (applies_to.lower() in ("stg_customers", "stg_orders", "stg_support") or applies_to == "(none)" or applies_to == "crm_addresses"):
            where_sqls.append(pred)

    select_list = ",\n       ".join(_select_expr(c) for c in model.column_mapping if c.get("target_column"))

    sql = [
        f"SELECT\n       {select_list}\nFROM ${{ref('{from_table}')}}"
    ]
    if join_sqls:
        sql.append("\n".join(join_sqls))
    if where_sqls:
        sql.append("\nWHERE " + " AND ".join(where_sqls))
    return "\n".join(sql)


def _build_final_sql(model: ModelSpec) -> str:
    if model.aggregations:
        select_list = []
        for a in model.aggregations:
            col = a.get("metric_column", "")
            formula = a.get("formula", "")
            if col and formula:
                select_list.append(f"{formula} AS {col}")
        group_by = model.group_by or []
        group_sql = "\nGROUP BY " + ", ".join(group_by) if group_by else ""
        return (
            "SELECT\n       "
            + ",\n       ".join(select_list)
            + "\nFROM ${{ref('stg_orders')}}"
            + group_sql
        )
    # If no aggregations, treat like staging pass-through
    return _build_staging_sql(model)


def build_sqlx_from_model(model: ModelSpec, staging_schema: str, final_schema: str) -> str:
    schema = staging_schema if model.layer == "staging" else final_schema
    config = (
        "config {\n"
        f"  type: \"table\",\n  schema: \"{schema}\"\n"
        "}\n\n"
    )

    # Simple approach: for staging, one final select built from mapping/joins/filters.
    # For final models with aggregations, build direct final select; otherwise pass-through.
    final_select = (
        _build_staging_sql(model) if model.layer == "staging" else _build_final_sql(model)
    )
    return config + final_select + "\n"
