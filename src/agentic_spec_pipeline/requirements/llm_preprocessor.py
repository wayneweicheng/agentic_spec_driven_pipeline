from __future__ import annotations
from typing import Any, Dict, List
import importlib
import pkgutil
import inspect
import os

SYSTEM_INSTRUCTION = (
    "You convert a data pipeline requirements Markdown (prose + tables) into a structured JSON spec. "
    "Output strictly JSON with keys: schema {raw_schema, staging_schema, final_schema}, "
    "models: [ {name, layer, sources, column_mapping, joins, filters, aggregations, group_by, constraints} ]. "
    "Do not include SQL code in the output, only expressions as needed in column_mapping.transform or aggregations.formula. "
    "Respect table names as provided."
)


def _load_gemini():
    # First try common explicit paths
    candidates = [
        ("google.adk.models.google", "Gemini"),
        ("google.adk.models.gemini", "Gemini"),
        ("google.adk.models", "Gemini"),
        ("adk.models.google", "Gemini"),
        ("adk.models.gemini", "Gemini"),
        ("adk.models", "Gemini"),
    ]
    for module_name, class_name in candidates:
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name, None)
            if cls is not None:
                return cls
        except ModuleNotFoundError:
            continue
        except Exception:
            continue

    # Walk packages to discover Gemini class dynamically
    pkg_names = ["google.adk", "adk"]
    for pkg_name in pkg_names:
        try:
            pkg = importlib.import_module(pkg_name)
            if hasattr(pkg, "Gemini") and inspect.isclass(getattr(pkg, "Gemini")):
                return getattr(pkg, "Gemini")
            if hasattr(pkg, "models"):
                models_mod = getattr(pkg, "models")
                if hasattr(models_mod, "Gemini") and inspect.isclass(getattr(models_mod, "Gemini")):
                    return getattr(models_mod, "Gemini")
            if hasattr(pkg, "__path__"):
                for _, modname, _ in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
                    try:
                        mod = importlib.import_module(modname)
                        if hasattr(mod, "Gemini") and inspect.isclass(getattr(mod, "Gemini")):
                            return getattr(mod, "Gemini")
                    except Exception:
                        continue
        except ModuleNotFoundError:
            continue
        except Exception:
            continue

    return None


def _call_llm_with_adk(markdown_text: str, model_name: str) -> str:
    Gemini = _load_gemini()
    if Gemini is None:
        raise ModuleNotFoundError("Gemini class not found in ADK")
    model = Gemini(name=model_name)
    prompt = (
        SYSTEM_INSTRUCTION
        + "\n\nRequirements Markdown:\n\n"
        + markdown_text
        + "\n\nReturn only valid JSON."
    )
    # Try known method names
    for meth in ("generate", "generate_content", "generate_text", "invoke", "run"):
        if hasattr(model, meth):
            resp = getattr(model, meth)(prompt)
            return resp.text if hasattr(resp, "text") else str(resp)
    if callable(model):
        resp = model(prompt)
        return resp.text if hasattr(resp, "text") else str(resp)
    raise AttributeError("ADK Gemini model has no known generation method")


def _call_llm_with_genai(markdown_text: str, model_name: str) -> str:
    try:
        import google.generativeai as genai
        from google.api_core.exceptions import NotFound
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "google-generativeai not installed. Install with `pip install google-generativeai` or `pip install -e .[llm]`."
        ) from e

    # Load .env if available
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except Exception:
        pass

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("GOOGLE_API_KEY is not set for google-generativeai usage")

    genai.configure(api_key=api_key)

    prompt = (
        SYSTEM_INSTRUCTION
        + "\n\nRequirements Markdown:\n\n"
        + markdown_text
        + "\n\nReturn only valid JSON."
    )

    # Try requested model first, then fall back to known supported IDs
    candidates: List[str] = [model_name, "gemini-2.0-flash", "gemini-1.5-pro-latest", "gemini-1.5-flash-latest"]
    last_err: Exception | None = None
    for m in candidates:
        try:
            model = genai.GenerativeModel(m)
            resp = model.generate_content(prompt)
            return resp.text or ""
        except NotFound as e:
            last_err = e
            continue
        except Exception as e:
            last_err = e
            continue
    if last_err:
        raise last_err
    raise RuntimeError("LLM call failed with no exception info")


def llm_preprocess_requirements(markdown_text: str, model_name: str = "gemini-2.0-flash") -> Dict[str, Any]:
    # Try ADK first; fallback to google-generativeai
    try:
        text = _call_llm_with_adk(markdown_text, model_name)
    except Exception:
        text = _call_llm_with_genai(markdown_text, model_name)

    # Simple JSON extraction: assume the model returns pure JSON per instruction
    import json

    text = (text or "").strip()
    try:
        data = json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            data = json.loads(text[start : end + 1])
        else:
            raise ValueError("LLM did not return valid JSON spec")

    data.setdefault("schema", {})
    data["schema"].setdefault("raw_schema", "raw")
    data["schema"].setdefault("staging_schema", "temp")
    data["schema"].setdefault("final_schema", "analytics")
    data.setdefault("models", [])
    return data
