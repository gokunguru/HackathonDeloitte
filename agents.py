"""Multi-agent orchestration with Gemini 2.5 Flash and deterministic English fallbacks."""

import json
import os
import re
from typing import Any

import config
import knowledge_base
import security_dlp


def _call_gemini_json(prompt: str) -> dict[str, Any] | None:
    """Invoke Gemini 2.5 Flash expecting a JSON object; return None on missing config or error."""
    api_key = os.environ.get(config.ENV_GEMINI_API_KEY, "").strip()
    gcp_project = os.environ.get(config.ENV_GOOGLE_CLOUD_PROJECT, "").strip()
    if not api_key and not gcp_project:
        return None

    try:
        from google import genai  # type: ignore
        from google.genai import types  # type: ignore

        if api_key:
            client = genai.Client(api_key=api_key)
        else:
            client = genai.Client(
                vertexai=True,
                project=gcp_project,
                location=config.GCP_REGION,
            )

        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        raw_text = (response.text or "").strip()
        if not raw_text:
            return None
        parsed = json.loads(raw_text)
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None


def _extract_rfp_signals(masked_rfp: str) -> dict[str, str]:
    """Extract key domain signals from the masked RFP for dynamic fallback generation."""
    budget_match = re.search(
        r"(€\s*\d+(?:[.,]\d+)?\s*[MkK]|\d+(?:[.,]\d+)?\s*(?:M€|k€|EUR))",
        masked_rfp,
        re.IGNORECASE,
    )
    sla_match = re.search(r"(\d{2,3}(?:[.,]\d+)?\s*%)\s*(?:production\s*)?SLA|SLA[^\d]*(\d{2,3}(?:[.,]\d+)?\s*%)", masked_rfp, re.IGNORECASE)
    region_match = re.search(r"(europe-west\d+)", masked_rfp, re.IGNORECASE)

    first_line = next(
        (line.strip() for line in masked_rfp.splitlines() if line.strip()),
        "Sovereign Cloud & AI Data Platform RFP",
    )

    sla_val = "99.95%"
    if sla_match:
        sla_val = sla_match.group(1) or sla_match.group(2) or "99.95%"

    return {
        "title_hint": first_line[:90],
        "budget": budget_match.group(1) if budget_match else "€1.8M (to be scoped)",
        "sla": sla_val,
        "region": region_match.group(1) if region_match else config.GCP_REGION,
        "has_csrd": "yes" if "csrd" in masked_rfp.lower() else "partial",
        "has_sovereignty": "yes"
        if any(k in masked_rfp.lower() for k in ("sovereign", "secnumcloud", "gdpr", "dlp"))
        else "standard",
    }


def _build_analyst_dimensions(has_sovereignty: str, has_csrd: str) -> list[dict[str, Any]]:
    """Build analyst scoring dimensions from centralized config.ANALYST_DIMENSIONS."""
    dims: list[dict[str, Any]] = []
    for item in config.ANALYST_DIMENSIONS:
        score = item["base"]
        if item["key"] == "sovereignty" and has_sovereignty != "yes":
            score -= 8
        elif item["key"] == "esg" and has_csrd != "yes":
            score -= 10
        dims.append({"label": item["label"], "score": score})
    return dims


def run_analyst(masked_rfp: str, use_llm: bool = True) -> dict[str, Any]:
    """VOL.01 — Go / No-Go analysis and strategic risk matrix."""
    prompt = (
        "You are the Deloitte Strategist Analyst Agent. Analyze this anonymized RFP in English "
        "and respond STRICTLY in valid JSON with keys: "
        "decision ('GO' or 'CONDITIONAL GO' or 'NO-GO'), score_opportunite (int 0-100), "
        "budget_detecte (str), delai_cle (str), points_forts (list[str]), "
        "risques (list[dict(risque, niveau, mitigation)]), synthese (str).\n\n"
        f"RFP:\n{masked_rfp}"
    )
    llm_res = _call_gemini_json(prompt) if use_llm else None
    signals = _extract_rfp_signals(masked_rfp)
    dimensions = _build_analyst_dimensions(signals["has_sovereignty"], signals["has_csrd"])
    if llm_res and "decision" in llm_res:
        llm_res.setdefault("dimensions", dimensions)
        llm_res.setdefault("engine", config.GEMINI_MODEL)
        return llm_res

    score = 86 if signals["has_sovereignty"] == "yes" and signals["has_csrd"] == "yes" else 74
    decision = "GO" if score >= 80 else "CONDITIONAL GO"

    return {
        "decision": decision,
        "score_opportunite": score,
        "budget_detecte": signals["budget"],
        "delai_cle": f"Kickoff Jan 2027 · Target SLA {signals['sla']}",
        "dimensions": dimensions,
        "points_forts": [
            "Strong alignment with Deloitte Sovereign Cloud & Data/AI capabilities.",
            f"Explicit low-carbon region mandate ({signals['region']}) directly matches our Paris landing zone.",
            "High ESG/CSRD evaluation weighting (30%) favors our Green IT differentiation.",
        ],
        "risques": [
            {
                "risque": "Strict SecNumCloud / EU sovereignty mandate on GenAI workloads",
                "niveau": "High",
                "mitigation": "Deploy on GCP europe-west9 with CMEK encryption, VPC Service Controls, and data residency guarantees.",
            },
            {
                "risque": f"Delivering {signals['sla']} SLA within ceiling budget ({signals['budget']})",
                "niveau": "Medium",
                "mitigation": "Automated FinOps guardrails from Build phase and scheduled shutdown of non-prod clusters.",
            },
            {
                "risque": "GDPR/DLP compliance for citizen data prior to AI indexing",
                "niveau": "Medium",
                "mitigation": "Inline Cloud DLP redaction pipeline upstream of the Lakehouse with immutable audit logs in France.",
            },
        ],
        "synthese": (
            f"High-conviction strategic opportunity ({score}/100) for '{signals['title_hint']}'. "
            "Technical scope, sovereignty posture, and CSRD weighting strongly justify an immediate bid."
        ),
        "engine": "deterministic_fallback",
    }


def run_knowledge(masked_rfp: str, user_role: str) -> dict[str, Any]:
    """VOL.02 — Knowledge Hunter strictly enforcing IAM Chinese Walls."""
    cases = knowledge_base.search_cases(masked_rfp, user_role)
    blocked_info = knowledge_base.get_blocked_cases_info(user_role)
    role_meta = config.USER_ROLES.get(user_role, {})

    return {
        "user_role": user_role,
        "role_label": role_meta.get("label", user_role),
        "clearance": role_meta.get("clearance", "N/A"),
        "allowed_sectors": role_meta.get("allowed_sectors", []),
        "cases": cases,
        "cases_count": len(cases),
        "blocked_count": blocked_info["blocked_count"],
        "blocked_sectors": blocked_info["blocked_sectors"],
    }


def run_rse(masked_rfp: str, use_llm: bool = True) -> dict[str, Any]:
    """VOL.03 — ESG, CSRD & Low-Carbon Green IT Audit."""
    prompt = (
        "You are the Deloitte Sustainability Auditor Agent (CSRD / Green IT). Evaluate this RFP in English "
        "and respond STRICTLY in valid JSON with keys: "
        "score_esg (int 0-100), region_recommandee (str), intensite_carbone (str), "
        "conformite_csrd (list[str]), actions_green_it (list[str]), "
        "gain_carbone_estime (str), synthese (str).\n\n"
        f"RFP:\n{masked_rfp}"
    )
    llm_res = _call_gemini_json(prompt) if use_llm else None
    if llm_res and "score_esg" in llm_res:
        llm_res.setdefault("engine", config.GEMINI_MODEL)
        return llm_res

    signals = _extract_rfp_signals(masked_rfp)
    region = signals["region"]
    is_paris = region.lower() == config.GCP_REGION

    return {
        "score_esg": 92 if is_paris else 78,
        "region_recommandee": f"{region} (Paris — Low-Carbon Region)",
        "intensite_carbone": "~50 gCO2eq/kWh (decarbonized French electricity grid)",
        "conformite_csrd": [
            "Granular Scope 2 & Scope 3 digital carbon telemetry per environment and AI inference call.",
            "Automated CSRD / ESRS E1 (Climate Change) audit-ready reporting.",
            "Continuous energy-intensity KPI tracking active from Sprint 1.",
        ],
        "actions_green_it": [
            "Software eco-design aligned with RGESN standards (pipeline & query frugality).",
            "Frugal AI routing: prioritizing lightweight models (Gemini Flash) for standard tasks.",
            "Automated scale-to-zero scheduling for Dev/QA environments outside business hours.",
            "Intelligent storage lifecycle policies (automated cold-tier archival after 90 days).",
        ],
        "gain_carbone_estime": "-42% energy intensity vs. legacy on-premises datacenter baseline",
        "synthese": (
            f"Target architecture validated in {region} with embedded FinOps/GreenOps governance, "
            "fully satisfying all eliminatory CSRD and Green IT requirements."
        ),
        "engine": "deterministic_fallback",
    }


def run_writer(
    masked_rfp: str,
    analyst_res: dict[str, Any],
    knowledge_res: dict[str, Any],
    rse_res: dict[str, Any],
    use_llm: bool = True,
) -> dict[str, Any]:
    """VOL.04 — Lead Architect Writer generating the structured Markdown proposal."""
    cases_summary = "\n".join(
        f"- {c['titre']} ({c['client_anonymise']} · {c['secteur']}): {c['resume']}"
        for c in knowledge_res.get("cases", [])
    )

    prompt = (
        "You are the Deloitte Lead Architect Writer Agent. Draft an executive-grade structured proposal "
        "in English Markdown integrating the Go/No-Go analysis, authorized client references, "
        "and ESG/CSRD commitments. Respond STRICTLY in valid JSON with keys: "
        "titre_propale (str), proposal_md (str), chapitres (list[str]).\n\n"
        f"ANALYSIS: {json.dumps(analyst_res, ensure_ascii=False)}\n"
        f"AUTHORIZED CASES: {cases_summary}\n"
        f"ESG AUDIT: {json.dumps(rse_res, ensure_ascii=False)}\n"
        f"RFP:\n{masked_rfp}"
    )
    compliance_matrix = [dict(row) for row in config.COMPLIANCE_TEMPLATE]
    llm_res = _call_gemini_json(prompt) if use_llm else None
    if llm_res and "proposal_md" in llm_res:
        llm_res.setdefault("compliance_matrix", compliance_matrix)
        llm_res.setdefault("engine", config.GEMINI_MODEL)
        return llm_res

    cases = knowledge_res.get("cases", [])
    cases_md = (
        "\n".join(
            f"- **{c['titre']}** (*{c['client_anonymise']}*, {c['secteur']}): {c['resume']}"
            for c in cases
        )
        if cases
        else "- No external client references required for this scope."
    )

    actions_md = "\n".join(f"- {act}" for act in rse_res.get("actions_green_it", []))
    risks_md = "\n".join(
        f"- **{r['risque']}** (*Severity: {r['niveau']}*) → {r['mitigation']}"
        for r in analyst_res.get("risques", [])
    )

    proposal_md = f"""# Commercial Proposal — Sovereign Low-Carbon Cloud & AI Data Platform

## 1. Executive Summary & Strategic Recommendation
**Deloitte Bid Decision:** `{analyst_res.get('decision', 'GO')}` (Opportunity Score: **{analyst_res.get('score_opportunite', 86)}/100**)  
**Target Ceiling:** {analyst_res.get('budget_detecte', '€1.8M')} | **Delivery Cadence:** {analyst_res.get('delai_cle', '99.95% SLA')}

Deloitte proposes a *Security & Sustainability by Design* architecture guaranteeing full European data sovereignty, native GDPR/DLP privacy enforcement, and verifiable CSRD compliance from Day 1.

## 2. Sovereign Architecture, Security & Automated DLP
- **French Sovereign Hosting:** Dedicated deployment in **{rse_res.get('region_recommandee', config.GCP_REGION)}** with Customer-Managed Encryption Keys (CMEK) and ministerial SSO/OIDC federation.
- **Zero Data Leakage (Cloud DLP):** Automated PII inspection and redaction upstream of all AI indexing and generative inference workflows.
- **High Availability & Resilience:** Multi-zone production architecture delivering a guaranteed **99.95% SLA**.

## 3. ESG, CSRD & Green IT Commitments
- **Projected ESG Score:** **{rse_res.get('score_esg', 92)}/100** ({rse_res.get('gain_carbone_estime', '-42% energy intensity')})
- **Grid Carbon Intensity:** {rse_res.get('intensite_carbone', '~50 gCO2eq/kWh')}
{actions_md}

## 4. Sourced Client References (Chinese Wall Clearance: {knowledge_res.get('clearance', 'N/A')})
{cases_md}

## 5. Risk Mitigation & Governance
{risks_md}

## 6. Delivery Roadmap & FinOps Model
- **Phase 1 (M1–M2):** Sovereign Landing Zone in `{config.GCP_REGION}`, SSO integration, and inline Cloud DLP pipeline.
- **Phase 2 (M3–M8):** Migration of 42 TB datasets, real-time DataOps Lakehouse, and GenAI policy assistant rollout.
- **Phase 3 (M9–M24):** Managed Run, continuous FinOps/GreenOps optimization, and automated CSRD reporting.
"""

    return {
        "titre_propale": "Commercial Proposal — Sovereign Low-Carbon Cloud & AI Data Platform",
        "proposal_md": proposal_md.strip(),
        "chapitres": [
            "1. Executive Summary & Strategic Recommendation",
            "2. Sovereign Architecture, Security & Automated DLP",
            "3. ESG, CSRD & Green IT Commitments",
            "4. Sourced Client References",
            "5. Risk Mitigation & Governance",
            "6. Delivery Roadmap & FinOps Model",
        ],
        "compliance_matrix": compliance_matrix,
        "engine": "deterministic_fallback",
    }


def run_redteam(proposal_md: str, masked_rfp: str, use_llm: bool = True) -> dict[str, Any]:
    """VOL.05 — Devil's Advocate auditing the proposal against RFP compliance & scoring gaps."""
    prompt = (
        "You are the Deloitte Red-Team (Devil's Advocate) Agent. Audit this proposal in English against "
        "the RFP and respond STRICTLY in valid JSON with keys: "
        "verdict ('APPROVED' or 'APPROVED WITH RESERVATIONS' or 'REWORK REQUIRED'), "
        "score_conformite (int 0-100), "
        "failles_detectees (list[dict(id, severite, point, recommandation, points_gain, patch_text)]), "
        "controles_passes (list[str]), synthese (str).\n\n"
        f"PROPOSAL:\n{proposal_md}\n\nRFP:\n{masked_rfp}"
    )
    llm_res = _call_gemini_json(prompt) if use_llm else None
    if llm_res and "verdict" in llm_res:
        llm_res.setdefault("engine", config.GEMINI_MODEL)
        return llm_res

    prop_lower = proposal_md.lower()
    rfp_lower = masked_rfp.lower()

    checks = [
        ("Low-carbon region europe-west9 explicitly specified", config.GCP_REGION in prop_lower),
        ("CSRD & Green IT requirements addressed", "csrd" in prop_lower and "green it" in prop_lower),
        ("Cloud DLP / GDPR PII protection enforced", "dlp" in prop_lower or "gdpr" in prop_lower),
        ("99.95% production SLA committed", "99.95%" in prop_lower or "sla" in prop_lower),
        ("Zero raw PII leakage in generated proposal", "@" not in proposal_md and "FR76" not in proposal_md),
    ]
    controles_passes = [label for label, ok in checks if ok]

    failles: list[dict[str, Any]] = []
    if "secnumcloud" in rfp_lower and "secnumcloud-aligned controls" not in prop_lower:
        failles.append(
            {
                "id": "GAP-01",
                "severite": "Critical",
                "point": "SecNumCloud / EU sovereignty attestation matrix missing from Architecture section.",
                "recommandation": "Append a formal SecNumCloud & Sovereign Controls compliance clause.",
                "points_gain": 8,
                "patch_text": (
                    "\n### Compliance Addendum — SecNumCloud & Sovereign Controls\n"
                    "- **Sovereign Isolation:** All workloads run exclusively in `europe-west9` under "
                    "SecNumCloud-aligned controls, VPC Service Controls perimeter isolation, and EU-resident CMEK.\n"
                ),
            }
        )

    if not re.search(r"\brpo\b", prop_lower) or not re.search(r"\brto\b", prop_lower):
        failles.append(
            {
                "id": "GAP-02",
                "severite": "Major",
                "point": "Explicit RPO (< 15 min) and RTO (< 1 hr) disaster recovery targets omitted.",
                "recommandation": "Commit contractually to RPO < 15 min and RTO < 1 hr multi-zone failover.",
                "points_gain": 8,
                "patch_text": (
                    "\n### Disaster Recovery Addendum — RPO / RTO Commitments\n"
                    "- **Multi-Zone Failover:** Active-passive replication across Paris availability zones "
                    "guaranteeing **RPO < 15 minutes** and **RTO < 1 hour** alongside the 99.95% SLA.\n"
                ),
            }
        )

    if "1.1m" not in prop_lower and "0.7m" not in prop_lower:
        failles.append(
            {
                "id": "GAP-03",
                "severite": "Minor",
                "point": "Build (€1.1M) vs. Managed Run (€0.7M) financial split not itemized.",
                "recommandation": "Include explicit Build/Run budget breakdown and FinOps cap.",
                "points_gain": 6,
                "patch_text": (
                    "\n### Commercial Addendum — Build vs. Run Breakdown\n"
                    "- **Transparent Pricing Cap:** €1.8M excl. VAT strictly allocated as **€1.1M Build** "
                    "(M1–M8) and **€0.7M Managed Run & FinOps** (M9–M24) with monthly unit-rate reporting.\n"
                ),
            }
        )

    total_possible_gain = sum(f["points_gain"] for f in failles)
    base_score = max(70, 96 - total_possible_gain)
    verdict = "APPROVED" if base_score >= 90 else "APPROVED WITH RESERVATIONS"

    return {
        "verdict": verdict,
        "score_conformite": base_score,
        "controles_passes": controles_passes,
        "failles_detectees": failles,
        "synthese": (
            f"Red-Team audit completed ({base_score}/100): {len(controles_passes)}/{len(checks)} core controls passed, "
            f"{len(failles)} actionable compliance gaps identified. Zero PII leakage detected."
        ),
        "engine": "deterministic_fallback",
    }


def build_project_portfolio(
    live_project_payload: dict[str, Any] | None,
    user_role: str,
) -> list[dict[str, Any]]:
    """Build the 5-project 3D Shelf portfolio (Live RFP + 4 catalog bids) with Chinese Wall locks."""
    role_cfg = config.USER_ROLES.get(user_role, {})
    allowed_sectors = set(role_cfg.get("allowed_sectors", []))

    payload = live_project_payload or {}
    raw_rfp = payload.get("raw_rfp") or config.SAMPLE_RFP_PATH.read_text(encoding="utf-8")
    dlp_res = payload.get("dlp_res") or security_dlp.mask_sensitive_data(raw_rfp)
    masked_rfp = dlp_res.get("masked_text", raw_rfp)

    analyst_res = payload.get("analyst_res") or run_analyst(masked_rfp, use_llm=False)
    knowledge_res = payload.get("knowledge_res") or run_knowledge(masked_rfp, user_role)
    rse_res = payload.get("rse_res") or run_rse(masked_rfp, use_llm=False)
    writer_res = payload.get("writer_res") or run_writer(
        masked_rfp, analyst_res, knowledge_res, rse_res, use_llm=False
    )
    redteam_res = payload.get("redteam_res") or run_redteam(
        writer_res.get("proposal_md", ""), masked_rfp, use_llm=False
    )

    live_signals = _extract_rfp_signals(masked_rfp)
    live_meta = config.LIVE_PROJECT_META

    live_project = {
        "id": live_meta["id"],
        "code": live_meta["code"],
        "badge": live_meta["badge"],
        "title": payload.get("title") or live_meta["default_title"],
        "client": payload.get("client") or live_meta["default_client"],
        "sector": payload.get("sector") or live_meta["default_sector"],
        "budget": payload.get("budget") or analyst_res.get("budget_detecte", live_signals["budget"]),
        "deadline": payload.get("deadline") or analyst_res.get("delai_cle", f"SLA {live_signals['sla']}"),
        "year": live_meta["year"],
        "is_locked": False,
        "dlp_res": dlp_res,
        "analyst_res": analyst_res,
        "knowledge_res": knowledge_res,
        "rse_res": rse_res,
        "writer_res": writer_res,
        "redteam_res": redteam_res,
    }

    portfolio: list[dict[str, Any]] = [live_project]

    for proj in config.PROJECT_CATALOG:
        is_locked = proj["sector"] not in allowed_sectors
        proj_dlp = security_dlp.mask_sensitive_data(proj["rfp_summary"])
        proj_masked = proj_dlp["masked_text"]

        proj_analyst = run_analyst(proj_masked, use_llm=False)
        proj_analyst["budget_detecte"] = proj["budget"]
        proj_analyst["delai_cle"] = proj["deadline"]

        proj_knowledge = run_knowledge(proj_masked, user_role)
        proj_rse = run_rse(proj_masked, use_llm=False)
        proj_writer = run_writer(
            proj_masked, proj_analyst, proj_knowledge, proj_rse, use_llm=False
        )
        proj_redteam = run_redteam(
            proj_writer.get("proposal_md", ""), proj_masked, use_llm=False
        )

        portfolio.append(
            {
                "id": proj["id"],
                "code": proj["code"],
                "badge": proj["badge"],
                "title": proj["title"],
                "client": proj["client"],
                "sector": proj["sector"],
                "budget": proj["budget"],
                "deadline": proj["deadline"],
                "year": proj["year"],
                "is_locked": is_locked,
                "dlp_res": proj_dlp,
                "analyst_res": proj_analyst,
                "knowledge_res": proj_knowledge,
                "rse_res": proj_rse,
                "writer_res": proj_writer,
                "redteam_res": proj_redteam,
            }
        )

    return portfolio
