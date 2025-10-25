from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse

from .requirements.parser import parse_requirements_markdown
from .requirements.spec_writer import write_spec_artifacts
from .requirements.llm_preprocessor import llm_preprocess_requirements
from .requirements.sqlx_generator import generate_sqlx_from_requirements
from .requirements.llm_sqlx_generator import generate_sqlx_with_llm
from .requirements.test_generator import generate_tests_from_requirements
from .requirements.llm_test_generator import generate_tests_with_llm

app = FastAPI(title="ADK Dataform Agent Web")

DEFAULT_MODEL = os.getenv("ADK_DEFAULT_MODEL", "gemini-2.0-flash")


@app.post("/spec-from-req")
async def spec_from_req(
    file: UploadFile,
    out_root: str = Form("examples/technical_requirements"),
    use_llm: bool = Form(False),
    model: str = Form(DEFAULT_MODEL),
):
    md_text = (await file.read()).decode("utf-8")
    if use_llm:
        data = llm_preprocess_requirements(md_text, model_name=model)
    else:
        data = parse_requirements_markdown(md_text)
    definitions_dir = Path(out_root) / "definitions"
    artifacts = write_spec_artifacts(data, definitions_dir)
    return JSONResponse({
        "spec_json": str(artifacts["spec_json"]),
        "mapping_docs": [str(p) for p in artifacts["mapping_docs"]],
    })


@app.post("/sqlx-from-spec")
async def sqlx_from_spec(
    spec_json: UploadFile,
    out_dir: str = Form("examples/pipeline_code/definitions"),
    use_llm: bool = Form(False),
    model: str = Form(DEFAULT_MODEL),
):
    data = json.loads((await spec_json.read()).decode("utf-8"))
    out_path = Path(out_dir)
    if use_llm:
        written = generate_sqlx_with_llm(data, out_path, model)
    else:
        last = generate_sqlx_from_requirements(data, out_path)
        written = [str(last)]
    return JSONResponse({"written": written})


@app.post("/tests-from-spec")
async def tests_from_spec(
    spec_json: UploadFile,
    out_dir: str = Form("examples/tests"),
    req_source: Optional[UploadFile] = None,
    use_llm: bool = Form(False),
    model: str = Form(DEFAULT_MODEL),
):
    data = json.loads((await spec_json.read()).decode("utf-8"))
    out_path = Path(out_dir)
    if use_llm:
        written = generate_tests_with_llm(data, out_path, model)
    else:
        source_text = None
        if req_source is not None:
            source_text = (await req_source.read()).decode("utf-8")
        written = generate_tests_from_requirements(data, out_path, source=source_text or "uploaded")
    return JSONResponse({"written": written})
