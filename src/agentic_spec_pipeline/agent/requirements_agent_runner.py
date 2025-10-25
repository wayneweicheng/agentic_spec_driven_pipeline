from pathlib import Path
from typing import Any, Dict

from adk.agents import LlmAgent
from adk.models.google import Gemini
from adk.sessions import InMemorySessionService

from ..requirements.parser import parse_requirements_markdown
from ..requirements.sqlx_generator import generate_sqlx_from_requirements
from ..requirements.test_generator import generate_tests_from_requirements


class ParseRequirementsTool:
    name = "parse_requirements"

    def __call__(self, markdown_text: str) -> Dict[str, Any]:
        return parse_requirements_markdown(markdown_text)


class GenerateSqlxFromReqTool:
    name = "generate_sqlx_from_requirements"

    def __call__(self, req: Dict[str, Any], out_dir: str) -> Dict[str, Any]:
        out_path = generate_sqlx_from_requirements(req, Path(out_dir))
        return {"sqlx": str(out_path)}


class GenerateTestsFromReqTool:
    name = "generate_tests_from_requirements"

    def __call__(self, req: Dict[str, Any], out_dir: str, source_path: str) -> Dict[str, Any]:
        written = generate_tests_from_requirements(req, Path(out_dir), Path(source_path))
        return {"written": written}


def build_requirements_agent() -> LlmAgent:
    model = Gemini(name="gemini-2.0-flash")
    session_service = InMemorySessionService()

    tools = [
        ParseRequirementsTool(),
        GenerateSqlxFromReqTool(),
        GenerateTestsFromReqTool(),
    ]

    agent = LlmAgent(
        name="dataform-req-agent",
        description=(
            "Agent that reads a requirements Markdown, generates SQLX and tests"
        ),
        instruction=(
            "Parse requirements YAML from Markdown, generate SQLX and minimal tests."
        ),
        model=model,
        tools=tools,
        session_service=session_service,
    )
    return agent
