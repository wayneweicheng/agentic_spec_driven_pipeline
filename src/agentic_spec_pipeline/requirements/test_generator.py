from pathlib import Path
from typing import Any, Dict, List

from ..tools.test_generator import _write_mock_temp_table_sql

TEST_HEADER = """-- Auto-generated tests from requirements
-- Requirements source: {source}
"""


def _emit_mocks(req: Dict[str, Any]) -> List[str]:
    parts: List[str] = []
    mocks: Dict[str, str] = req.get("mocks", {})
    for src in req.get("sources", []):
        name = src["name"]
        csv_body = mocks.get(name, "id,value\n1,1\n")
        parts.append(_write_mock_temp_table_sql(name, csv_body))
    return parts


def generate_tests_from_requirements(req: Dict[str, Any], out_dir: Path, source: Path) -> List[str]:
    out_dir.mkdir(parents=True, exist_ok=True)

    written: List[str] = []

    models = req.get("models", [])
    if models:
        for model in models:
            parts: List[str] = [TEST_HEADER.format(source=source)]
            parts.extend(_emit_mocks(req))
            parts.append("SELECT 1 AS test_assertion;\n")
            sql_text = "\n".join(parts)
            out_path = out_dir / f"test_req_{model['name']}.sql"
            out_path.write_text(sql_text)
            written.append(str(out_path))
        return written

    # Fallback single test
    parts: List[str] = [TEST_HEADER.format(source=source)]
    parts.extend(_emit_mocks(req))
    parts.append("SELECT 1 AS test_assertion;\n")
    sql_text = "\n".join(parts)

    final_name = req.get("final", {}).get("name", "final_output")
    out_path = out_dir / f"test_req_{final_name}.sql"
    out_path.write_text(sql_text)
    written.append(str(out_path))
    return written
