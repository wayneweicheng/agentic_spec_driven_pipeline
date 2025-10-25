from pathlib import Path
from typing import Dict, List

TEST_HEADER = """-- Auto-generated test for {cte}
-- Source file: {source}
-- NOTE: Replace inline temp tables with richer mock datasets as needed.
"""


def _write_mock_temp_table_sql(table_name: str, csv_body: str) -> str:
    lines = csv_body.strip().splitlines()
    headers = lines[0].split(",")
    values = lines[1:]
    rows_sql = []
    for v in values:
        cols = v.split(",")
        quoted = [f"'{c}'" for c in cols]
        rows_sql.append(f"SELECT {', '.join(quoted)}")
    union_all = "\nUNION ALL\n".join(rows_sql) if rows_sql else "SELECT NULL AS placeholder"
    select_alias = ", ".join([f"{h}" for h in headers])
    return (
        f"WITH {table_name} AS (\n"
        f"  SELECT {select_alias} FROM (\n{_indent(union_all, 4)}\n  )\n)\n"
    )


def _indent(text: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(pad + line for line in text.splitlines())


def generate_bq_tests(
    file_path: Path,
    ctes: List[str],
    refs: List[str],
    output_dir: Path,
    fixtures: Dict[str, str],
) -> List[str]:
    """Generate per-CTE BigQuery test scripts using inline temp tables for mocks."""
    written: List[str] = []

    for cte in ctes or ["final_output"]:
        parts = [TEST_HEADER.format(cte=cte, source=file_path)]
        # Inline mock temp tables
        for table_name, csv_body in fixtures.items():
            parts.append(_write_mock_temp_table_sql(table_name, csv_body))
        # Minimal assertion placeholder
        parts.append(
            "SELECT 1 AS test_assertion -- TODO: replace with real assertions against CTE output\n"
        )
        sql_text = "\n".join(parts)
        out_path = output_dir / f"test_{file_path.stem}_{cte}.sql"
        out_path.write_text(sql_text)
        written.append(str(out_path))

    return written
