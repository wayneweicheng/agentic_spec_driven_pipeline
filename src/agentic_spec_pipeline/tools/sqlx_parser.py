import re
from typing import Dict, List

REF_PATTERN = re.compile(r"\$\{\s*ref\(\s*'([^']+)'\s*\)\s*\}")
CTE_NAME_PATTERN = re.compile(r"(?mi)^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s*\(")


def extract_ctes_and_refs(sqlx_text: str) -> Dict[str, List[str]]:
    """
    Extract CTE names and ${ref('table')} references from a SQLX file's text.
    This is a pragmatic parser that handles common patterns.
    """
    refs = REF_PATTERN.findall(sqlx_text)

    ctes: List[str] = []

    # Find the WITH block (if any), then capture CTE names in that block
    with_idx = re.search(r"(?mi)\bWITH\b", sqlx_text)
    if with_idx:
        # Take substring starting at WITH to end; find occurrences of `<name> AS (` at line starts
        with_sub = sqlx_text[with_idx.start() :]
        for match in CTE_NAME_PATTERN.finditer(with_sub):
            cte_name = match.group(2)
            ctes.append(cte_name)

    return {"ctes": ctes, "refs": sorted(set(refs))}
