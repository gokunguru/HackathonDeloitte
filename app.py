"""Main Streamlit application for Deloitte Secure Bid Squad."""

from io import BytesIO
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

import agents
import config
import security_dlp
import shelf_component

st.set_page_config(
    page_title="Deloitte Secure Bid Squad",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _inject_supabase_css() -> None:
    """Apply Supabase Dark Precision styling to Streamlit chrome."""
    t = config.SUPABASE_THEME
    st.markdown(
        f"""
        <style>
          .stApp {{
            background-color: {t["bg"]};
            color: {t["text"]};
          }}
          .block-container {{
            padding-top: 3.2rem;
            padding-bottom: 1rem;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
            max-width: 100%;
          }}
          section[data-testid="stSidebar"] {{
            background-color: {t["card"]};
            border-right: 1px solid {t["border"]};
          }}
          section[data-testid="stSidebar"] .stMarkdown,
          section[data-testid="stSidebar"] label {{
            color: {t["text"]};
          }}
          .stButton > button[kind="primary"] {{
            background-color: {t["accent"]};
            color: #0d1612;
            border: 1px solid {t["accent"]};
            font-weight: 700;
            border-radius: 4px;
          }}
          .stButton > button[kind="primary"]:hover {{
            background-color: {t["mint"]};
            border-color: {t["mint"]};
            color: #0d1612;
          }}
          .dlp-banner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            background: {t["card"]};
            border: 1px solid {t["border"]};
            border-left: 3px solid {t["accent"]};
            border-radius: 4px;
            padding: 10px 16px;
            margin-bottom: 8px;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: 13px;
            color: {t["text"]};
          }}
          .dlp-badge {{
            background: rgba(62, 207, 142, 0.12);
            border: 1px solid rgba(62, 207, 142, 0.4);
            color: {t["accent"]};
            padding: 3px 9px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
          }}
          .agent-progress-strip {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
            background: {t["card"]};
            border: 1px solid {t["border"]};
            border-radius: 4px;
            padding: 7px 14px;
            margin-bottom: 8px;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: 11px;
          }}
          .agent-step-pill {{
            color: {t["accent"]};
            background: rgba(62, 207, 142, 0.08);
            border: 1px solid rgba(62, 207, 142, 0.3);
            padding: 2px 8px;
            border-radius: 3px;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _extract_uploaded_text(uploaded_file: Any) -> str:
    """Extract UTF-8 text from an uploaded .txt or .pdf file."""
    if uploaded_file is None:
        return ""
    filename = (uploaded_file.name or "").lower()
    raw_bytes = uploaded_file.getvalue()
    if filename.endswith(".pdf"):
        try:
            from pypdf import PdfReader  # type: ignore

            reader = PdfReader(BytesIO(raw_bytes))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages).strip()
        except Exception as exc:
            st.warning(f"Partial PDF extraction ({exc}). Falling back to raw UTF-8 decode.")
            return raw_bytes.decode("utf-8", errors="ignore")
    return raw_bytes.decode("utf-8", errors="ignore")


def _load_sample_rfp() -> str:
    """Load the built-in sample RFP text."""
    if config.SAMPLE_RFP_PATH.exists():
        return config.SAMPLE_RFP_PATH.read_text(encoding="utf-8")
    return (
        "RFP: Sovereign Low-Carbon Data & AI Platform (1.8M EUR, SLA 99.95%, "
        "europe-west9 region, CSRD 30% weighting)."
    )


def _normalize_project(proj: dict[str, Any]) -> dict[str, Any]:
    """Normalize a portfolio project entry into the schema consumed by shelf_component."""
    dlp_res = proj.get("dlp_res", {})
    analyst_res = proj.get("analyst_res", {})
    knowledge_res = proj.get("knowledge_res", {})
    rse_res = proj.get("rse_res", {})
    writer_res = proj.get("writer_res", {})
    redteam_res = proj.get("redteam_res", {})

    reqs = [
        {"title": pt, "priority": "STRATEGIC", "status": "Deloitte Aligned"}
        for pt in analyst_res.get("points_forts", [])
    ]
    if analyst_res.get("budget_detecte"):
        reqs.append(
            {
                "title": f"Target Budget: {analyst_res['budget_detecte']}",
                "priority": "FINOPS",
                "status": analyst_res.get("delai_cle", "Scoped"),
            }
        )

    risks = [
        {
            "title": r.get("risque", ""),
            "severity": r.get("niveau", "Medium"),
            "mitigation": r.get("mitigation", ""),
        }
        for r in analyst_res.get("risques", [])
    ]

    case_items = [
        {
            "title": c.get("titre", "Client Case"),
            "client": c.get("client_anonymise", "Confidential Client"),
            "sector": c.get("secteur", ""),
            "summary": c.get("resume", ""),
            "source": c.get("source_file", ""),
            "impact": f"{c.get('client_anonymise', '')} · Verified reference",
        }
        for c in knowledge_res.get("cases", [])
    ]

    low_carbon_args = list(rse_res.get("actions_green_it", []))
    if rse_res.get("intensite_carbone"):
        low_carbon_args.insert(0, f"Carbon intensity: {rse_res['intensite_carbone']}")
    if rse_res.get("gain_carbone_estime"):
        low_carbon_args.insert(1, f"Estimated impact: {rse_res['gain_carbone_estime']}")

    vulnerabilities = []
    for idx, faille in enumerate(redteam_res.get("failles_detectees", []), start=1):
        sev = str(faille.get("severite", "Minor"))
        default_gain = 10 if "maj" in sev.lower() or "high" in sev.lower() or "crit" in sev.lower() else 6
        gain = int(faille.get("points_gain", faille.get("penalty", default_gain)))
        patch_text = faille.get("patch_text", faille.get("recommandation", "Contractual clause added."))
        vulnerabilities.append(
            {
                "id": faille.get("id", f"GAP-{idx:02d}"),
                "title": faille.get("point", f"Finding #{idx}"),
                "severity": sev,
                "points_gain": gain,
                "penalty": gain,
                "critique": faille.get("point", ""),
                "patch_text": patch_text,
            }
        )

    return {
        "id": proj.get("id", "proj_live"),
        "code": proj.get("code", "PROJ-LIVE"),
        "badge": proj.get("badge", "LIVE RFP"),
        "title": proj.get("title", "Sovereign Bid"),
        "client": proj.get("client", "Enterprise Client"),
        "sector": proj.get("sector", "Public Sector"),
        "budget": proj.get("budget", "€1.8M"),
        "deadline": proj.get("deadline", "SLA 99.95%"),
        "year": proj.get("year", "2026"),
        "is_locked": bool(proj.get("is_locked", False)),
        "dlp": {
            "masked_count": dlp_res.get("findings_count", 0),
            "details": dlp_res.get("details", []),
        },
        "go_nogo": {
            "score": analyst_res.get("score_opportunite", 82),
            "decision": analyst_res.get("decision", "GO"),
            "summary": analyst_res.get("synthese", ""),
            "requirements": reqs,
            "risks": risks,
        },
        "cases": {
            "items": case_items,
            "blocked_count": knowledge_res.get("blocked_count", 0),
            "blocked_sectors": knowledge_res.get("blocked_sectors", []),
        },
        "rse": {
            "score": rse_res.get("score_esg", 88),
            "summary": rse_res.get("synthese", ""),
            "csrd_criteria": rse_res.get("conformite_csrd", []),
            "low_carbon_args": low_carbon_args,
            "region": config.GCP_REGION,
        },
        "propale": {
            "markdown": writer_res.get("proposal_md", ""),
            "filename": f"{str(proj.get('code', 'proposal')).lower()}_proposal.md",
        },
        "redteam": {
            "initial_score": redteam_res.get("score_conformite", 74),
            "summary": redteam_res.get("synthese", ""),
            "controles_passes": redteam_res.get("controles_passes", []),
            "vulnerabilities": vulnerabilities,
        },
    }


def _build_shelf_payload(
    role_key: str,
    portfolio: list[dict[str, Any]],
) -> dict[str, Any]:
    """Assemble the full 5-project shelf payload for shelf_component."""
    role_meta = config.USER_ROLES.get(role_key, {})
    return {
        "role_key": role_key,
        "role_label": role_meta.get("label", role_key),
        "clearance": role_meta.get("clearance", "LEVEL 2"),
        "allowed_sectors": role_meta.get("allowed_sectors", []),
        "dimensions": config.ANALYST_DIMENSIONS,
        "compliance_template": config.COMPLIANCE_TEMPLATE,
        "projects": [_normalize_project(p) for p in portfolio],
    }


def _run_pipeline(raw_rfp: str, role_key: str) -> None:
    """Execute the 5-agent pipeline on the live RFP and build the 5-project portfolio."""
    progress_bar = st.progress(0, text="Initialisation de Secure Bid Squad...")
    with st.status("Exécution du pipeline Secure Bid Squad...", expanded=True) as status:
        progress_bar.progress(10, text="Étape 0/5 — 🛡️ Sas Sécurité Cloud DLP...")
        st.write("⏳ **0/5** — 🛡️ Sas Sécurité Cloud DLP (masquage PII)...")
        dlp_res = security_dlp.mask_sensitive_data(raw_rfp)
        masked_rfp = dlp_res["masked_text"]
        st.write(f"✅ **0/5** — Cloud DLP : {dlp_res.get('findings_count', 0)} donnée(s) sensible(s) masquée(s)")

        progress_bar.progress(25, text="Étape 1/5 — 🧠 Agent Analyste Stratège (Go/No-Go)...")
        st.write("⏳ **1/5** — 🧠 Analyste Stratège (exigences, risques, Go/No-Go)...")
        analyst_res = agents.run_analyst(masked_rfp)
        st.write(f"✅ **1/5** — Analyste terminé (Décision : {analyst_res.get('decision', 'GO')})")

        progress_bar.progress(45, text="Étape 2/5 — 🔍 Agent Chasseur de Savoir (IAM Chinese Wall)...")
        st.write("⏳ **2/5** — 🔍 Chasseur de Savoir (recherche cas clients & IAM)...")
        knowledge_res = agents.run_knowledge(masked_rfp, role_key)
        st.write(f"✅ **2/5** — {len(knowledge_res)} cas client(s) sourcé(s)")

        progress_bar.progress(60, text="Étape 3/5 — 🌱 Agent Auditeur RSE / ESG...")
        st.write("⏳ **3/5** — 🌱 Auditeur RSE / ESG (CSRD, Green Cloud)...")
        rse_res = agents.run_rse(masked_rfp)
        st.write(f"✅ **3/5** — Score RSE : {rse_res.get('score_rse', 'N/A')}/100")

        progress_bar.progress(80, text="Étape 4/5 — ✍️ Agent Architecte Rédacteur...")
        st.write("⏳ **4/5** — ✍️ Architecte Rédacteur (matrice de conformité & propale)...")
        writer_res = agents.run_writer(masked_rfp, analyst_res, knowledge_res, rse_res)
        st.write("✅ **4/5** — Brouillon de propale généré")

        progress_bar.progress(92, text="Étape 5/5 — 😈 Agent Red-Team (Audit acheteur)...")
        st.write("⏳ **5/5** — 😈 Avocat du Diable / Red-Team (notation & failles)...")
        redteam_res = agents.run_redteam(writer_res.get("proposal_md", ""), masked_rfp)
        st.write(f"✅ **5/5** — Audit Red-Team terminé ({redteam_res.get('note_sur_20', 'N/A')}/20)")

        live_project_payload = {
            "raw_rfp": raw_rfp,
            "dlp_res": dlp_res,
            "analyst_res": analyst_res,
            "knowledge_res": knowledge_res,
            "rse_res": rse_res,
            "writer_res": writer_res,
            "redteam_res": redteam_res,
        }
        portfolio = agents.build_project_portfolio(live_project_payload, role_key)

        progress_bar.progress(100, text="✅ Pipeline Secure Bid Squad terminé !")
        status.update(
            label="✅ Pipeline Secure Bid Squad terminé — 5 projets prêts",
            state="complete",
            expanded=False,
        )
    progress_bar.empty()

    st.session_state["raw_rfp"] = raw_rfp
    st.session_state["masked_rfp"] = masked_rfp
    st.session_state["dlp_res"] = dlp_res
    st.session_state["shelf_payload"] = _build_shelf_payload(role_key, portfolio)


def main() -> None:
    """Render sidebar controls, live security strip, and the 3D Bid Project Shelf."""
    _inject_supabase_css()

    with st.sidebar:
        st.markdown(f"### {config.APP_TITLE}")
        st.caption(config.APP_SUBTITLE)
        st.divider()

        role_keys = list(config.USER_ROLES.keys())
        selected_role = st.selectbox(
            "IAM Profile & Clearance",
            options=role_keys,
            format_func=lambda k: config.USER_ROLES[k]["label"],
            index=0,
        )
        role_info = config.USER_ROLES[selected_role]
        st.caption(
            f"Clearance: **{role_info['clearance']}** · "
            f"Sectors: {', '.join(role_info['allowed_sectors'])}"
        )

        st.divider()
        use_sample = st.checkbox(
            "Use built-in sample RFP",
            value=True,
        )
        uploaded_file = st.file_uploader(
            "Upload RFP (.txt or .pdf)",
            type=["txt", "pdf"],
            disabled=use_sample,
        )

        launch_clicked = st.button(
            "Launch Secure Bid Squad",
            type="primary",
            use_container_width=True,
        )

    raw_rfp = _load_sample_rfp() if use_sample or uploaded_file is None else _extract_uploaded_text(uploaded_file)

    if launch_clicked or "shelf_payload" not in st.session_state:
        _run_pipeline(raw_rfp, selected_role)

    shelf_payload = st.session_state["shelf_payload"]
    dlp_res = st.session_state["dlp_res"]
    masked_count = dlp_res.get("findings_count", 0)
    live_proj = shelf_payload["projects"][0]

    st.markdown(
        f"""
        <div class="dlp-banner">
          <div>
            <strong>Cloud DLP: {masked_count} sensitive items masked before LLM inference</strong>
            <span style="color:{config.SUPABASE_THEME['muted']};margin-left:10px;">
              Zero PII leakage · Region {config.GCP_REGION}
            </span>
          </div>
          <span class="dlp-badge">{shelf_payload['role_label']} · {shelf_payload['clearance']}</span>
        </div>
        <div class="agent-progress-strip">
          <span style="color:{config.SUPABASE_THEME['smoke']};font-weight:700;">LIVE PIPELINE:</span>
          <span class="agent-step-pill">1. Strategist ✓</span>
          <span class="agent-step-pill">2. Knowledge ✓</span>
          <span class="agent-step-pill">3. ESG ✓</span>
          <span class="agent-step-pill">4. Architect ✓</span>
          <span class="agent-step-pill">5. Red-Team ✓</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Inspect live Cloud DLP Audit (Before / After)", expanded=False):
        col_before, col_after = st.columns(2)
        with col_before:
            st.caption("Before (Raw RFP Document)")
            st.code(st.session_state.get("raw_rfp", ""), language="text")
        with col_after:
            st.caption("After (De-identified stream sent to agents)")
            st.code(st.session_state.get("masked_rfp", ""), language="text")
        if dlp_res.get("details"):
            st.dataframe(dlp_res["details"], use_container_width=True, hide_index=True)

    shelf_html = shelf_component.render_shelf_html(shelf_payload)
    components.html(shelf_html, height=780, scrolling=False)

    st.download_button(
        label="Download Live Proposal (.md)",
        data=live_proj["propale"]["markdown"],
        file_name=live_proj["propale"]["filename"],
        mime="text/markdown",
    )


if __name__ == "__main__":
    main()
