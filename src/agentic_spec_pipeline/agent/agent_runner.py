from pathlib import Path
from typing import Any, Dict

from adk.agents import LlmAgent
from adk.models.google import Gemini
from adk.sessions import InMemorySessionService

from ..tools.sqlx_parser import extract_ctes_and_refs
from ..tools.mock_data import generate_mock_fixtures
from ..tools.test_generator import generate_bq_tests


class ParseSqlxTool:
    name = "parse_sqlx"

    def __call__(self, sqlx_text: str) -> Dict[str, Any]:
        return extract_ctes_and_refs(sqlx_text)


class GenerateMockDataTool:
    name = "generate_mock_data"

    def __call__(self, refs: list[str], rows: int = 5) -> Dict[str, str]:
        return generate_mock_fixtures(refs, num_rows=rows)


class WriteBqTestsTool:
    name = "write_bq_tests"

    def __call__(
        self,
        source_path: str,
        ctes: list[str],
        refs: list[str],
        output_dir: str,
        fixtures: Dict[str, str],
    ) -> Dict[str, Any]:
        written = generate_bq_tests(
            file_path=Path(source_path),
            ctes=ctes,
            refs=refs,
            output_dir=Path(output_dir),
            fixtures=fixtures,
        )
        return {"written": written}


def build_agent() -> LlmAgent:
    model = Gemini(name="gemini-2.0-flash")
    session_service = InMemorySessionService()

    tools = [ParseSqlxTool(), GenerateMockDataTool(), WriteBqTestsTool()]

    agent = LlmAgent(
        name="dataform-test-agent",
        description=(
            "Agent that generates Dataform SQLX CTE-level tests with mock data"
        ),
        instruction=(
            "Analyze SQLX, extract CTEs and refs, create mock data, and emit tests."
        ),
        model=model,
        tools=tools,
        session_service=session_service,
    )
    return agent
