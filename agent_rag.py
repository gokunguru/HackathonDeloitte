import re
from pathlib import Path
from typing import List, Dict

CASES_DIR = Path(__file__).parent / "data" / "cases"

STOPWORDS = {
    "le", "la", "les", "un", "une", "des", "du", "de", "d", "et", "ou", "en",
    "dans", "pour", "par", "sur", "avec", "sans", "au", "aux", "ce", "ces",
    "est", "sont", "a", "ont", "the", "and", "or", "for", "with", "in", "on",
    "to", "of", "rfp", "appel", "offres", "projet", "client", "mission",
}

ROLE_LEVELS = {
    "stagiaire": 1,
    "junior": 1,
    "consultant": 1,
    "consulting_banque": 2,
    "senior": 2,
    "manager": 3,
    "senior manager": 4,
    "director": 5,
    "directeur": 5,
    "partner": 6,
    "associe": 6,
    "associé": 6,
    "restricted_defense": 6,
    "admin": 6,
}

CONFIDENTIALITY_REQUIRED_LEVEL = {
    "public": 1,
    "interne": 1,
    "standard": 1,
    "ouvert": 1,
    "restreint": 3,
    "confidentiel": 3,
    "manager": 3,
    "chinese_wall": 5,
    "chinese wall": 5,
    "strict": 5,
    "secret": 6,
    "partner": 6,
    "m&a": 6,
}


def _get_role_level(user_role: str) -> int:
    role_norm = (user_role or "consultant").strip().lower()
    for key, level in ROLE_LEVELS.items():
        if key in role_norm:
            return level
    return 1


def _extract_field(content: str, patterns: List[str], default: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, content, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            val = match.group(1).strip().strip("*_`\"'")
            if val:
                return val
    return default


def _parse_case_file(file_path: Path) -> Dict:
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = [line.strip() for line in content.splitlines() if line.strip()]

    titre = file_path.stem.replace("_", " ").title()
    for line in lines:
        if line.startswith("#"):
            titre = line.lstrip("#").strip()
            break

    secteur = _extract_field(
        content, [r"secteur\s*:\s*(.+)", r"industry\s*:\s*(.+)"], default="Multi-secteurs"
    )
    client_anonymise = _extract_field(
        content, [r"client(?:\s*\(anonymis[ée]\)|_anonymise)?\s*:\s*(.+)", r"compte\s*:\s*(.+)"], default="Grand Compte Confidentiel"
    )
    confidentialite = _extract_field(
        content,
        [
            r"confidentialit[ée]\s*:\s*(.+)",
            r"niveau(?:_acces)?\s*:\s*(.+)",
            r"chinese\s*wall\s*:\s*(.+)",
            r"iam\s*:\s*(.+)",
        ],
        default="interne",
    )

    resume = _extract_field(
        content, [r"r[ée]sum[ée]\s*:\s*(.+)", r"impact\s*:\s*(.+)"], default=""
    )
    if not resume:
        body_lines = [
            l for l in lines
            if not l.startswith("#")
            and not re.match(r"^(secteur|client|confidentialit|niveau|iam|---|\*\*secteur|\*\*client)", l, re.I)
        ]
        resume = " ".join(body_lines)[:280].strip()
        if len(" ".join(body_lines)) > 280:
            resume += "..."

    conf_norm = confidentialite.lower()
    required_level = 1
    for key, lvl in CONFIDENTIALITY_REQUIRED_LEVEL.items():
        if key in conf_norm:
            required_level = max(required_level, lvl)

    return {
        "titre": titre,
        "client_anonymise": client_anonymise,
        "secteur": secteur,
        "resume": resume,
        "source_file": file_path.name,
        "niveau_confidentialite": confidentialite,
        "_required_level": required_level,
        "_raw_content": content,
        "_full_text": content.lower(),
    }


def _tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-zàâäéèêëïîôöùûüç0-9]{3,}", text.lower())
    return [w for w in words if w not in STOPWORDS]


def search_cases(query: str, user_role: str = "Consulting_Banque") -> List[Dict]:
    """
    Agent 2 — RAG Interne & Chinese Walls.
    Lit data/cases/, filtre selon les droits IAM du `user_role`,
    et retourne les 3 meilleurs cas clients sourcés.
    """
    if not CASES_DIR.exists():
        return []

    user_level = _get_role_level(user_role)
    query_tokens = _tokenize(query or "")

    authorized_cases = []
    for file_path in sorted(CASES_DIR.glob("*.md")):
        if "charte_rse" in file_path.name.lower():
            continue

        case = _parse_case_file(file_path)

        # Chinese Wall strict pour les dossiers Défense / compartimentés
        if "Restricted_Defense" in case["_raw_content"] and user_role != "Restricted_Defense":
            continue

        if user_level < case["_required_level"]:
            continue

        score = 0
        header_text = f"{case['titre']} {case['secteur']}".lower()
        body_text = case["_full_text"]
        for tok in query_tokens:
            if tok in header_text:
                score += 3
            if tok in body_text:
                score += 1

        authorized_cases.append((score, case))

    authorized_cases.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "titre": case["titre"],
            "client_anonymise": case["client_anonymise"],
            "secteur": case["secteur"],
            "resume": case["resume"],
            "source_file": case["source_file"],
            "niveau_confidentialite": case["niveau_confidentialite"],
            "score_pertinence": score,
        }
        for score, case in authorized_cases[:3]
    ]