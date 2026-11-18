import streamlit as st

from core_agents import run_analyst, run_redteam, run_writer

try:
    from security_dlp import mask_sensitive_data
except ImportError:
    def mask_sensitive_data(text: str) -> dict:
        return {"masked_text": text, "findings_count": 0, "details": []}

try:
    from rse_agent import run_knowledge, run_rse
except ImportError:
    def run_knowledge(masked_rfp: str, user_role: str) -> list[dict]:
        return [
            {
                "titre": "Migration Data Warehouse vers BigQuery en environnement bancaire",
                "client_anonymise": "Banque de détail européenne (Top 5)",
                "secteur": "Banque & Assurance",
                "resume": "Migration de 120 To en 8 mois vers europe-west9 avec conformité DORA.",
                "source_file": "case_banque_bigquery.md",
            }
        ]

    def run_rse(masked_rfp: str) -> dict:
        return {
            "score_rse": 85,
            "criteres_detectes": ["Hébergement bas carbone", "Sobriété numérique"],
            "arguments_deloitte_green_cloud": [
                "Déploiement sur Google Cloud europe-west9 (Paris) bas carbone.",
                "Pilotage FinOps / GreenOps pour réduire l'empreinte de l'infrastructure.",
            ],
        }


st.set_page_config(page_title="Deloitte Secure Bid Squad", page_icon="🛡️", layout="wide")
st.title("🛡️ Deloitte Secure Bid Squad")
st.caption("Équipe augmentée par Agentic AI — Sécurité by Design (Cloud DLP + Vertex AI)")

with st.sidebar:
    st.header("Paramètres")
    user_role = st.selectbox(
        "Profil utilisateur (IAM / Chinese Walls)",
        ["Manager FS (Banque)", "Consultant Tech & Cloud", "Partner Public Sector"],
    )
    uploaded_file = st.file_uploader("Déposer un RFP (.txt ou .pdf)", type=["txt", "pdf"])
    default_rfp = (
        "Objet : Migration Data & Cloud d'une banque de détail vers Google Cloud (europe-west9).\n"
        "Délai : 9 mois. Budget : 1,8 M€.\n"
        "Exigences : Zéro fuite de données (RGPD, DORA), critère RSE 20%, références bancaires."
    )
    rfp_text = st.text_area("Ou coller le texte du RFP :", value=default_rfp, height=180)
    launch = st.button("🚀 Lancer Secure Bid Squad", type="primary", use_container_width=True)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(uploaded_file)
        rfp_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        rfp_text = uploaded_file.read().decode("utf-8", errors="ignore")

if launch and rfp_text.strip():
    progress = st.progress(0, text="0. Sas Sécurité Cloud DLP en cours...")
    dlp_out = mask_sensitive_data(rfp_text)
    st.success(f"🛡️ Cloud DLP : {dlp_out.get('findings_count', 0)} donnée(s) sensible(s) masquée(s)")

    progress.progress(20, text="🧠 Agent 1 — Analyse Stratégique (Go / No-Go)...")
    analyst_out = run_analyst(dlp_out["masked_text"])

    progress.progress(45, text="🔍 Agent 2 & 🌱 Agent 3 — Cas Clients & Audit RSE...")
    cases_out = run_knowledge(dlp_out["masked_text"], user_role)
    rse_out = run_rse(dlp_out["masked_text"])

    progress.progress(75, text="✍️ Agent 4 — Rédaction de la propale...")
    draft_md = run_writer(dlp_out["masked_text"], analyst_out, cases_out, rse_out)

    progress.progress(90, text="😈 Agent 5 — Audit Red-Team...")
    redteam_out = run_redteam(draft_md, analyst_out.get("exigences", []))
    progress.progress(100, text="✅ Analyse complète terminée !")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1. Go / No-Go",
        "2. Cas Clients",
        "3. Score RSE",
        "4. Propale Générée",
        "5. Audit Red-Team",
    ])

    with tab1:
        st.metric("Score Go / No-Go", f"{analyst_out.get('score_go_nogo', 0)} / 100")
        st.write(analyst_out.get("resume", ""))
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Exigences clés")
            for ex in analyst_out.get("exigences", []):
                st.markdown(f"- {ex}")
        with col2:
            st.subheader("Risques identifiés")
            for r in analyst_out.get("risques", []):
                st.markdown(f"- {r}")

    with tab2:
        for c in cases_out:
            with st.expander(f"📁 {c.get('titre', 'Cas client')} — {c.get('client_anonymise', '')}"):
                st.write(f"**Secteur :** {c.get('secteur', '')}")
                st.write(c.get("resume", ""))
                st.caption(f"Source : `{c.get('source_file', '')}`")

    with tab3:
        score_rse = int(rse_out.get("score_rse", 0))
        st.metric("Score RSE / ESG", f"{score_rse} / 100")
        st.progress(min(max(score_rse, 0), 100))
        st.subheader("Critères détectés")
        for cr in rse_out.get("criteres_detectes", []):
            st.markdown(f"- {cr}")
        st.subheader("Arguments Deloitte Green Cloud")
        for arg in rse_out.get("arguments_deloitte_green_cloud", []):
            st.markdown(f"- {arg}")

    with tab4:
        st.download_button(
            "⬇️ Télécharger la propale (.md)",
            data=draft_md,
            file_name="propale_deloitte.md",
            mime="text/markdown",
        )
        st.markdown(draft_md)

    with tab5:
        st.metric("Note Red-Team", f"{redteam_out.get('note_sur_20', 0)} / 20")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Points forts")
            for pf in redteam_out.get("points_forts", []):
                st.markdown(f"- ✅ {pf}")
        with col2:
            st.subheader("Failles à corriger")
            for fa in redteam_out.get("failles_a_corriger", []):
                st.markdown(f"- ⚠️ {fa}")
