import os

def _load_env() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

_load_env()

__all__ = [
    "cli",
]
