# DELOITTE // SECURE BID SQUAD

**Augmented Bid War Room · Security by Design**

An enterprise multi-agent RFP response platform built with **Streamlit**, **Google Cloud DLP**, **IAM Chinese Walls**, and **Gemini 2.5 Flash**, engineered for sovereign, low-carbon deployment on **Google Cloud Run (`europe-west9`, Paris)**.

---

## Architecture Overview

```text
Raw RFP (PDF / TXT / Paste)
   │
   ▼
[1. Cloud DLP Privacy Airlock] ──► Masks PII (Names, Emails, Phones, IBANs)
   │
   ▼
[2. Multi-Agent Squad (Gemini 2.5 Flash)]
   ├── VOL.01 Strategist Analyst      ──► Go / No-Go & Risk Matrix
   ├── VOL.02 Knowledge Hunter        ──► Anonymized Cases (IAM Chinese Wall)
   ├── VOL.03 Sustainability Auditor  ──► CSRD & Green IT (europe-west9)
   ├── VOL.04 Lead Architect Writer   ──► Structured Executive Proposal
   └── VOL.05 Red-Team Advocate       ──► Compliance Audit & Interactive Patching
```

---

## Security by Design

1. **Zero-Leakage Cloud DLP Airlock (`security_dlp.py`)**
   - Automatically inspects and masks sensitive PII (`PERSON_NAME`, `EMAIL_ADDRESS`, `PHONE_NUMBER`, `IBAN_CODE`, `FRANCE_NIR`) via **Google Cloud DLP** when `GCP_PROJECT_ID` is configured, with a deterministic regex fallback for air-gapped local execution.
   - Raw PII never reaches LLM prompts or generated proposals.

2. **IAM Chinese Wall Enforcement (`knowledge_base.py`)**
   - Client case studies in `data/cases/` are strictly filtered by the active user's clearance level (`config.USER_ROLES`):
     - **Level 2 (`consultant_public`)**: Public Sector, Energy, Transport (Banking & Finance blocked).
     - **Level 3 (`manager_energie`)**: Energy, Industry, Public Sector (Banking & Finance blocked).
     - **Level 5 (`partner_finance`)**: Full cross-sector access.

---

## 5-Agent Pipeline & Gamified 3D Dossier Shelf UI

- **VOL.01 — Go / No-Go Analysis (`STRAT-01`)**: Evaluates strategic fit, budget ceiling, SLA feasibility, and risk mitigations.
- **VOL.02 — Sourced Client Cases (`KNOW-02`)**: Ranks top anonymized references under strict Chinese Wall enforcement.
- **VOL.03 — ESG & Low-Carbon Audit (`ESG-03`)**: Validates CSRD Scope 2/3 compliance, RGESN eco-design, and `europe-west9` (~50 gCO2eq/kWh) hosting.
- **VOL.04 — Structured Proposal (`PROP-04`)**: Synthesizes all findings into an executive Markdown deliverable.
- **VOL.05 — Red-Team Audit (`RED-05`)**: Scores proposal compliance (e.g., `74/100`) and provides one-click **Interactive Compliance Patches** (`+8`, `+8`, `+6`) to raise readiness to `96/100`.

---

## Business & ROI Impact

| Metric | Traditional Bid Process | Secure Bid Squad |
| :--- | :--- | :--- |
| **First-Draft Turnaround** | 5–7 business days | **< 90 seconds** |
| **PII Leakage Risk** | Manual redaction | **0% (Automated DLP Airlock)** |
| **Chinese Wall Compliance** | Honor system | **Programmatic IAM Filtering** |
| **ESG / CSRD Alignment** | Ad-hoc appendix | **Native Audit & Scoring** |

---

## Local Setup

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Configure Gemini / GCP DLP
export GEMINI_API_KEY="your-api-key"
export GCP_PROJECT_ID="your-gcp-project-id"

# 4. Launch the War Room
streamlit run app.py
```

---

## Google Cloud Run Deployment (`europe-west9`)

Deploy directly to the low-carbon Paris region (`europe-west9`):

```bash
gcloud run deploy secure-bid-squad \
  --source . \
  --region europe-west9 \
  --platform managed \
  --port 8080 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=your-gcp-project-id,GCP_PROJECT_ID=your-gcp-project-id"
```
