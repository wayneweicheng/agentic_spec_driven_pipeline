import json
import os
from pathlib import Path
import socket
from urllib.parse import urlparse
import typer

from .requirements.parser import parse_requirements_markdown
from .requirements.sqlx_generator import generate_sqlx_from_requirements
from .requirements.test_generator import generate_tests_from_requirements
from .requirements.spec_writer import write_spec_artifacts

app = typer.Typer(help="Specification-Driven Pipeline Agent CLI")

DEFAULT_MODEL = os.getenv("ADK_DEFAULT_MODEL", "gemini-2.0-flash")


def _normalize_emulator_endpoint(endpoint: str) -> str:
    if not endpoint:
        return endpoint
    # Accept forms like 127.0.0.1:9050 or http://127.0.0.1:9050[/]
    if "://" not in endpoint:
        endpoint = f"http://{endpoint}"
    # Strip trailing slash
    if endpoint.endswith("/"):
        endpoint = endpoint[:-1]
    return endpoint


def _preflight_port(endpoint: str, timeout_s: float = 2.0) -> None:
    parsed = urlparse(endpoint)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 9050
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout_s)
        try:
            s.connect((host, port))
        except Exception as e:
            raise typer.BadParameter(
                f"Emulator not reachable at {host}:{port}. Ensure it's running and listening."
            ) from e


@app.command("init-req")
def init_requirements(
    out: Path = typer.Option(Path("examples/business_requirements/customer_order_pipeline_requirement.md"), "--out", help="Path to write a sample requirements markdown"),
):
    """Write a sample requirements Markdown template."""
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        sample = (Path(__file__).parents[2] / "examples/business_requirements/customer_order_pipeline_requirement.md").read_text()
        out.write_text(sample)
        typer.echo(f"Wrote sample requirements to {out}")
    else:
        typer.echo(f"File already exists: {out}")


@app.command("spec-from-req")
def spec_from_req(
    req: Path = typer.Option(..., "--req", exists=True, readable=True, help="Path to requirements .md"),
    out_root: Path = typer.Option(Path("examples/technical_requirements"), "--out-root", help="Technical artifacts root (spec + mappings, not code)"),
    use_llm: bool = typer.Option(False, "--use-llm", help="Use LLM to preprocess requirements"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="LLM model name (e.g., gemini-2.5-flash)"),
):
    """Create spec.json and mapping docs from a requirements Markdown file (no SQLX)."""
    md_text = req.read_text()
    if use_llm:
        from .requirements.llm_preprocessor import llm_preprocess_requirements
        data = llm_preprocess_requirements(md_text, model_name=model)
    else:
        data = parse_requirements_markdown(md_text)

    definitions_dir = out_root / "definitions"
    artifacts = write_spec_artifacts(data, definitions_dir)
    typer.echo(f"Spec JSON: {artifacts['spec_json']}")
    typer.echo(f"Mapping docs: {len(artifacts['mapping_docs'])} -> {out_root / 'mappings'}")


@app.command("sqlx-from-spec")
def sqlx_from_spec(
    spec: Path = typer.Option(..., "--spec", exists=True, readable=True, help="Path to spec.json"),
    out_dir: Path = typer.Option(Path("examples/pipeline_code/definitions"), "--out-dir", help="Where to write generated SQLX code"),
    use_llm: bool = typer.Option(False, "--use-llm", help="Use LLM to synthesize complex SQLX"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="LLM model name (e.g., gemini-2.5-flash)"),
):
    """Generate SQLX files from a spec.json. If --use-llm, delegate to LLM-based generator."""
    data = json.loads(spec.read_text())
    if use_llm:
        from .requirements.llm_sqlx_generator import generate_sqlx_with_llm
        written = generate_sqlx_with_llm(data, out_dir, model)
        typer.echo(f"Generated SQLX (LLM): {len(written)} -> {out_dir}")
    else:
        sqlx_path = generate_sqlx_from_requirements(data, out_dir)
        typer.echo(f"Generated SQLX (last written): {sqlx_path}")


@app.command("tests-from-spec")
def tests_from_spec(
    spec: Path = typer.Option(..., "--spec", exists=True, readable=True, help="Path to spec.json"),
    out_dir: Path = typer.Option(Path("examples/tests"), "--out-dir", help="Where to write generated tests"),
    req_source: Path = typer.Option(None, "--req-source", help="Optional: original requirements .md for traceability"),
    use_llm: bool = typer.Option(False, "--use-llm", help="Use LLM to synthesize complex tests"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="LLM model name (e.g., gemini-2.5-flash)"),
):
    """Generate tests from a spec.json. If --use-llm, delegate to LLM-based test generator."""
    data = json.loads(spec.read_text())
    if use_llm:
        from .requirements.llm_test_generator import generate_tests_with_llm
        written = generate_tests_with_llm(data, out_dir, model)
        typer.echo(f"Generated tests (LLM): {len(written)} -> {out_dir}")
        return
    source = req_source if req_source else spec
    written = generate_tests_from_requirements(data, out_dir, source=source)
    typer.echo(f"Generated tests: {len(written)} -> {out_dir}")


@app.command("emulator-seed")
def emulator_seed(
    ddl_dir: Path = typer.Option(Path("examples/business_requirements/source_ddl"), "--ddl-dir", exists=True, file_okay=False, help="Directory of DDL .sql files to apply"),
    emulator_host: str = typer.Option(os.getenv("BIGQUERY_EMULATOR_HOST", "http://127.0.0.1:9050"), "--emulator-host", help="BigQuery emulator host (scheme+host:port)"),
    project: str = typer.Option("emulator-project", "--project", help="Project id for emulator namespaces"),
    timeout_sec: int = typer.Option(30, "--timeout-sec", help="Per-DDL timeout seconds"),
):
    """Apply DDLs to BigQuery emulator (goccy/bigquery-emulator)."""
    try:
        from google.cloud import bigquery
        from google.api_core.client_options import ClientOptions
        from google.auth.credentials import AnonymousCredentials
        from google.api_core.exceptions import GoogleAPIError
    except Exception as e:
        raise typer.BadParameter("Install BigQuery extras: pip install -e '.[bigquery]'") from e

    endpoint = _normalize_emulator_endpoint(emulator_host)
    _preflight_port(endpoint)
    typer.echo(f"Emulator endpoint: {endpoint}")

    client = bigquery.Client(
        project=project,
        credentials=AnonymousCredentials(),
        client_options=ClientOptions(api_endpoint=endpoint),
    )

    # Ensure datasets exist
    for dataset in ("raw", "temp", "analytics"):
        ds_id = f"{project}.{dataset}"
        try:
            client.get_dataset(ds_id)
            typer.echo(f"Dataset exists: {ds_id}")
        except Exception:
            client.create_dataset(ds_id)
            typer.echo(f"Created dataset: {ds_id}")

    ddls = sorted(ddl_dir.glob("*.sql"))
    for ddl in ddls:
        sql = ddl.read_text()
        typer.echo(f"APPLY {ddl.name}...")
        try:
            job = client.query(sql)
            job.result(timeout=timeout_sec)
            typer.echo(f"APPLIED {ddl.name}")
        except GoogleAPIError as ge:
            typer.echo(f"ERROR {ddl.name}: {ge}")
            raise
        except Exception as e:
            typer.echo(f"ERROR {ddl.name}: {e}")
            raise
    typer.echo("Emulator seeded with DDLs.")


@app.command("run-tests")
def run_tests(
    dir: Path = typer.Option(Path("examples/tests"), "--dir", exists=True, file_okay=False, help="Directory containing *.sql test files"),
    project: str = typer.Option(os.getenv("GOOGLE_CLOUD_PROJECT", ""), "--project", help="GCP project ID (uses GOOGLE_CLOUD_PROJECT if unset)"),
    location: str = typer.Option(os.getenv("GOOGLE_CLOUD_LOCATION", "US"), "--location", help="BigQuery location"),
    fail_fast: bool = typer.Option(True, "--fail-fast/--no-fail-fast", help="Stop on first failure"),
    emulator_host: str = typer.Option(os.getenv("BIGQUERY_EMULATOR_HOST", ""), "--emulator-host", help="If set, run against emulator (scheme+host:port)"),
):
    """Execute generated test SQL files. Supports real BigQuery or BigQuery emulator."""
    try:
        from google.cloud import bigquery
        from google.api_core.client_options import ClientOptions
        from google.auth.credentials import AnonymousCredentials
    except Exception as e:
        raise typer.BadParameter("Install BigQuery extras: pip install -e '.[bigquery]'\nAlso ensure gcloud auth (real BQ) OR provide emulator host.") from e

    if emulator_host:
        endpoint = _normalize_emulator_endpoint(emulator_host)
        _preflight_port(endpoint)
        if not project:
            project = "emulator-project"
        client = bigquery.Client(
            project=project,
            credentials=AnonymousCredentials(),
            client_options=ClientOptions(api_endpoint=endpoint),
        )
    else:
        if not project:
            raise typer.BadParameter("--project is required or set GOOGLE_CLOUD_PROJECT in env")
        client = bigquery.Client(project=project, location=location)

    tests = sorted([p for p in dir.glob("*.sql")])
    if not tests:
        typer.echo(f"No .sql tests found in {dir}")
        raise typer.Exit(0)

    results = []
    for path in tests:
        sql = path.read_text()
        try:
            job = client.query(sql, job_config=bigquery.QueryJobConfig(use_legacy_sql=False))
            job.result()
            results.append({"file": str(path), "status": "passed"})
            typer.echo(f"PASS {path.name}")
        except Exception as err:
            results.append({"file": str(path), "status": "failed", "error": str(err)})
            typer.echo(f"FAIL {path.name}: {err}")
            if fail_fast:
                break

    (dir / "results.json").write_text(json.dumps(results, indent=2))
    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")
    typer.echo(f"Completed. Passed: {passed}, Failed: {failed}. Results -> {dir / 'results.json'}")


@app.command("web")
def web(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
    reload: bool = typer.Option(False, "--reload"),
):
    """Run the FastAPI web server (requires .[web] extra)."""
    try:
        import uvicorn
    except Exception as e:
        raise typer.BadParameter("Install web extras: pip install -e '.[web]'") from e
    uvicorn.run("agentic_spec_pipeline.webapp:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
