"""Chinese-Wall-enforced knowledge base search over anonymized client cases."""

import re
from pathlib import Path
from typing import Any

import config


def _tokenize(text: str) -> set[str]:
    """Extract normalized alphanumeric tokens excluding common English stopwords."""
    tokens = set(re.findall(r"[a-z0-9]{3,}", text.lower()))
    return tokens - config.STOPWORDS


def _parse_case_file(path: Path) -> dict[str, str]:
    """Parse structured metadata headers and body from a case markdown file."""
    content = path.read_text(encoding="utf-8")
    meta = {
        "titre": path.stem,
        "client_anonymise": "Confidential Client",
        "secteur": "Unspecified",
        "resume": "",
        "source_file": path.name,
        "_full_text": content,
    }

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("Title:"):
            meta["titre"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Client:"):
            meta["client_anonymise"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Sector:"):
            meta["secteur"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("Summary:"):
            meta["resume"] = stripped.split(":", 1)[1].strip()

    return meta


def _load_all_cases() -> list[dict[str, str]]:
    """Load all markdown case files from config.CASES_DIR."""
    if not config.CASES_DIR.exists():
        return []
    files = sorted(config.CASES_DIR.glob(f"*{config.CASE_FILE_EXT}"))
    return [_parse_case_file(path) for path in files]


def _get_allowed_sectors(user_role: str) -> list[str]:
    """Resolve allowed sectors for a given role key, defaulting safely to empty."""
    role_cfg = config.USER_ROLES.get(user_role)
    if not role_cfg:
        return []
    return list(role_cfg.get("allowed_sectors", []))


def search_cases(query: str, user_role: str) -> list[dict[str, Any]]:
    """Search and rank anonymized cases strictly filtered by the user's Chinese Wall."""
    allowed_sectors = _get_allowed_sectors(user_role)
    if not allowed_sectors:
        return []

    query_tokens = _tokenize(query)
    all_cases = _load_all_cases()

    scored_cases: list[tuple[int, dict[str, Any]]] = []
    for case in all_cases:
        if case["secteur"] not in allowed_sectors:
            continue

        case_tokens = _tokenize(case["_full_text"])
        overlap_score = len(query_tokens & case_tokens)
        is_reference_charter = case["source_file"] == config.CHARTE_RSE_FILENAME
        tie_breaker = 0 if is_reference_charter else 1

        scored_cases.append(
            (
                overlap_score * 10 + tie_breaker,
                {
                    "titre": case["titre"],
                    "client_anonymise": case["client_anonymise"],
                    "secteur": case["secteur"],
                    "resume": case["resume"],
                    "source_file": case["source_file"],
                },
            )
        )

    scored_cases.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in scored_cases[: config.DEFAULT_TOP_CASES]]


def get_blocked_cases_info(user_role: str) -> dict[str, Any]:
    """Return count and sectors of cases blocked by Chinese Wall for UI indicators."""
    allowed_sectors = _get_allowed_sectors(user_role)
    all_cases = _load_all_cases()

    blocked_sectors: set[str] = set()
    blocked_count = 0
    for case in all_cases:
        if case["secteur"] not in allowed_sectors:
            blocked_count += 1
            blocked_sectors.add(case["secteur"])

    return {
        "blocked_count": blocked_count,
        "blocked_sectors": sorted(blocked_sectors),
    }
