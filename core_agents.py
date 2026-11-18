import json
import os
from typing import Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MODEL_ID = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _get_genai_client():
    """Initialize google-genai client (Vertex AI first, then API key fallback)."""
    try:
        from google import genai
    except ImportError:
        return None

    project = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "europe-west9")
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if project:
        return genai.Client(vertexai=True, project=project, location=location)
    if api_key:
        return genai.Client(api_key=api_key)
    return None


def _clean_json_response(raw_text: str) -> dict[str, Any]:
    """Parse JSON safely even if wrapped in markdown code fences."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)


# ==============================================================================
# AGENT 1 — ANALYSTE STRATÈGE
# ==============================================================================
def run_analyst(masked_rfp: str) -> dict[str, Any]:
    """
    Analyse un RFP anonymisé et retourne :
    - score_go_nogo: int (0 à 100)
    - resume: str
    - exigences: list[str]
    - risques: list[str]
    """
    client = _get_genai_client()
    if client is None:
        return _analyst_fallback(masked_rfp)

    from google.genai import types

    prompt = f"""
Tu es l'Agent 1 (Analyste Stratège) chez Deloitte Consulting (practice Avant-Vente / Bid Management).
Analyse l'appel d'offres (RFP) anonymisé ci-dessous et évalue l'opportunité.

Réponds UNIQUEMENT avec un objet JSON valide respectant exactement ce schéma :
{{
  "score_go_nogo": <entier entre 0 et 100 représentant la pertinence stratégique et faisabilité pour Deloitte>,
  "resume": "<synthèse exécutive claire en 3-4 phrases : client, objectif, budget/délais si mentionnés>",
  "exigences": [
    "<exigence clé technique, métier, sécurité ou RSE 1>",
    "<exigence clé 2>"
  ],
  "risques": [
    "<risque projet, juridique, délai serré ou contrainte critique 1>",
    "<risque 2>"
  ]
}}

Règles :
- Extrais entre 4 et 8 exigences concrètes.
- Identifie entre 3 et 6 risques majeurs.
- Ne mentionne aucune donnée personnelle qui aurait échappé au masquage.

RFP anonymisé :
\"\"\"
{masked_rfp}
\"\"\"
""".strip()

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )
        data = _clean_json_response(response.text)
        return {
            "score_go_nogo": int(data.get("score_go_nogo", 0)),
            "resume": str(data.get("resume", "")),
            "exigences": list(data.get("exigences", [])),
            "risques": list(data.get("risques", [])),
        }
    except Exception as exc:
        fallback = _analyst_fallback(masked_rfp)
        fallback["risques"].append(f"Mode dégradé activé (erreur LLM : {exc})")
        return fallback


def _analyst_fallback(masked_rfp: str) -> dict[str, Any]:
    """Fallback local si Vertex AI / Gemini n'est pas encore configuré."""
    word_count = len(masked_rfp.split())
    return {
        "score_go_nogo": 78,
        "resume": (
            f"Appel d'offres analysé en mode local ({word_count} mots). "
            "Opportunité alignée avec les offres Cloud, Data et Transformation de Deloitte."
        ),
        "exigences": [
            "Architecture Cloud sécurisée et souveraine (hébergement Europe).",
            "Conformité RGPD et protection des données sensibles.",
            "Accompagnement au changement et gouvernance projet.",
            "Critères RSE / Green IT à intégrer dans la réponse.",
        ],
        "risques": [
            "Délais de livraison potentiellement contraints.",
            "Exigences de sécurité/conformité élevées nécessitant une validation juridique.",
            "Clés GCP / Vertex AI non détectées : résultat généré via fallback local.",
        ],
    }


# ==============================================================================
# AGENT 4 — ARCHITECTE RÉDACTEUR
# ==============================================================================
def run_writer(
    masked_rfp: str,
    analyst_out: dict[str, Any],
    cases_out: list[dict[str, Any]],
    rse_out: dict[str, Any],
) -> str:
    """
    Génère la matrice de conformité et un premier jet structuré de la propale
    en Markdown à partir du RFP anonymisé et des sorties des Agents 1, 2 et 3.
    """
    client = _get_genai_client()
    if client is None:
        return _writer_fallback(analyst_out, cases_out, rse_out)

    from google.genai import types

    prompt = f"""
Tu es l'Agent 4 (Architecte Rédacteur) chez Deloitte Consulting.
Rédige une proposition commerciale (propale) structurée, convaincante et prête pour relecture par un Associé Deloitte, en format Markdown.

Tu dois t'appuyer UNIQUEMENT sur les éléments fournis ci-dessous (ne jamais inventer de fausses références clients ni de données personnelles).

### 1. Contexte du RFP anonymisé :
\"\"\"
{masked_rfp}
\"\"\"

### 2. Analyse Stratégique (Agent 1) :
{json.dumps(analyst_out, indent=2, ensure_ascii=False)}

### 3. Cas Clients Deloitte Sourcés (Agent 2 — Knowledge Base) :
{json.dumps(cases_out, indent=2, ensure_ascii=False)}

### 4. Audit & Arguments RSE / Green Cloud (Agent 3) :
{json.dumps(rse_out, indent=2, ensure_ascii=False)}

Structure obligatoire de la propale en Markdown :
1. **Synthèse Exécutive** (alignée sur les enjeux du client et la valeur Deloitte)
2. **Matrice de Conformité** (tableau Markdown : `Exigence du RFP | Réponse Deloitte | Statut`) couvrant toutes les exigences de l'Agent 1
3. **Architecture Cible & Approche de Delivery** (incluant la mitigation des risques identifiés)
4. **Nos Références Clients Pertinentes** (en citant explicitement les cas de l'Agent 2 et leur `source_file`)
5. **Engagement RSE & Green Cloud** (intégrant les arguments de l'Agent 3, ex. Google Cloud `europe-west9` bas carbone)
6. **Gouvernance, Planning & Prochaines Étapes**
""".strip()

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
            ),
        )
        text = (response.text or "").strip()
        if not text:
            return _writer_fallback(analyst_out, cases_out, rse_out)
        return text
    except Exception:
        return _writer_fallback(analyst_out, cases_out, rse_out)


def _writer_fallback(
    analyst_out: dict[str, Any],
    cases_out: list[dict[str, Any]],
    rse_out: dict[str, Any],
) -> str:
    exigences = analyst_out.get("exigences", [])
    rows = "\n".join(
        f"| {ex} | Couvert par l'offre Deloitte Cloud & Data | ✅ Conforme |"
        for ex in exigences
    ) or "| Exigences générales | Couvert par Deloitte | ✅ Conforme |"

    cases_md = "\n".join(
        f"- **{c.get('titre', 'Cas client')}** ({c.get('client_anonymise', 'Client')}, {c.get('secteur', 'Secteur')}) : {c.get('resume', '')} *(Source : {c.get('source_file', 'N/A')})*"
        for c in cases_out
    ) or "- Références en cours de consolidation."

    rse_args = "\n".join(
        f"- {arg}" for arg in rse_out.get("arguments_deloitte_green_cloud", [])
    ) or "- Déploiement optimisé sur Google Cloud `europe-west9` (Paris)."

    return f"""# Proposition Commerciale — Deloitte Consulting

## 1. Synthèse Exécutive
{analyst_out.get('resume', '')}

## 2. Matrice de Conformité
| Exigence du RFP | Réponse Deloitte | Statut |
| :--- | :--- | :--- |
{rows}

## 3. Nos Références Clients Pertinentes
{cases_md}

## 4. Engagement RSE & Green Cloud (Score RSE : {rse_out.get('score_rse', 'N/A')}/100)
{rse_args}
"""


# ==============================================================================
# AGENT 5 — AVOCAT DU DIABLE (RED-TEAM)
# ==============================================================================
def run_redteam(draft_md: str, exigences: list[str]) -> dict[str, Any]:
    """
    Évalue le brouillon de propale comme un acheteur client exigeant et retourne :
    - note_sur_20: float
    - points_forts: list[str]
    - failles_a_corriger: list[str]
    """
    client = _get_genai_client()
    if client is None:
        return _redteam_fallback(draft_md, exigences)

    from google.genai import types

    prompt = f"""
Tu es l'Agent 5 (Avocat du Diable / Red-Team) dans un comité d'évaluation client très exigeant.
Évalue la proposition commerciale (Markdown) ci-dessous par rapport aux exigences du RFP.

Réponds UNIQUEMENT avec un objet JSON valide respectant exactement ce schéma :
{{
  "note_sur_20": <nombre entre 0 et 20, ex: 15.5>,
  "points_forts": [
    "<point fort concret de la propale 1>",
    "<point fort 2>"
  ],
  "failles_a_corriger": [
    "<faille, oubli, promesse trop vague ou risque non traité à corriger avant envoi 1>",
    "<faille 2>"
  ]
}}

Règles :
- Sois critique, constructif et précis (vérifie si chaque exigence est vraiment chiffrée et prouvée).
- Donne entre 3 et 5 points forts, et entre 3 et 5 failles actionnables à corriger.

Exigences du RFP à vérifier :
{json.dumps(exigences, indent=2, ensure_ascii=False)}

Brouillon de propale :
\"\"\"
{draft_md}
\"\"\"
""".strip()

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )
        data = _clean_json_response(response.text)
        return {
            "note_sur_20": float(data.get("note_sur_20", 0)),
            "points_forts": list(data.get("points_forts", [])),
            "failles_a_corriger": list(data.get("failles_a_corriger", [])),
        }
    except Exception as exc:
        fallback = _redteam_fallback(draft_md, exigences)
        fallback["failles_a_corriger"].append(f"Mode dégradé activé (erreur LLM : {exc})")
        return fallback


def _redteam_fallback(draft_md: str, exigences: list[str]) -> dict[str, Any]:
    return {
        "note_sur_20": 14.5,
        "points_forts": [
            "Structure claire incluant une matrice de conformité.",
            "Prise en compte explicite du volet RSE / Green Cloud.",
            "Références clients structurées et sourcées.",
        ],
        "failles_a_corriger": [
            "Chiffrer davantage les engagements de délai (jalons à 3, 6 et 9 mois).",
            "Détailler le plan de réversibilité et la conformité DORA.",
            f"Vérifier la couverture exhaustive des {len(exigences)} exigences avant envoi.",
        ],
    }


if __name__ == "__main__":
    sample_rfp = """
    Objet : Appel d'offres - Migration Data & Cloud d'une banque de détail.
    Contact : [PERSON_NAME] ([EMAIL_ADDRESS]).
    Contexte : La banque souhaite migrer son entrepôt de données legacy vers Google Cloud
    (région Paris europe-west9) sous 9 mois. Budget indicatif : 1,8 M€.
    Exigences :
    - Zéro fuite de données bancaires (conformité RGPD, DORA, chiffrement).
    - Réduction de l'empreinte carbone de l'infrastructure (critère RSE : 20% de la note).
    - Références similaires exigées dans le secteur bancaire européen.
    """
    print("=== TEST AGENT 1 (ANALYSTE) ===")
    analyst_out = run_analyst(sample_rfp)
    print(json.dumps(analyst_out, indent=2, ensure_ascii=False))

    mock_cases = [
        {
            "titre": "Migration Data Warehouse vers BigQuery en environnement bancaire",
            "client_anonymise": "Banque de détail européenne (Top 5)",
            "secteur": "Banque & Assurance",
            "resume": "Migration de 120 To en 8 mois vers europe-west9 avec conformité DORA et -38% de coûts run.",
            "source_file": "case_banque_bigquery.md",
        }
    ]
    mock_rse = {
        "score_rse": 88,
        "criteres_detectes": ["Réduction empreinte carbone", "Hébergement bas carbone"],
        "arguments_deloitte_green_cloud": [
            "Déploiement sur Google Cloud europe-west9 (Paris) alimenté par un mix électrique très bas carbone.",
            "FinOps & GreenOps automatisés pour réduire les requêtes et le stockage inutiles (-35% d'empreinte).",
        ],
    }

    print("\n=== TEST AGENT 4 (WRITER) ===")
    draft_md = run_writer(sample_rfp, analyst_out, mock_cases, mock_rse)
    print(draft_md[:800] + "\n...[tronqué pour affichage]...")

    print("\n=== TEST AGENT 5 (RED-TEAM) ===")
    redteam_out = run_redteam(draft_md, analyst_out["exigences"])
    print(json.dumps(redteam_out, indent=2, ensure_ascii=False))
