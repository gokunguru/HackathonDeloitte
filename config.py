"""Centralized configuration and constants for Deloitte Secure Bid Squad."""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

APP_TITLE = "DELOITTE // SECURE BID SQUAD"
APP_SUBTITLE = "Augmented Bid War Room · Security by Design"
GCP_REGION = os.getenv("GOOGLE_CLOUD_LOCATION", "europe-west9")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CASES_DIR = DATA_DIR / "cases"
SAMPLE_RFP_PATH = DATA_DIR / "sample_rfp.txt"

ENV_GCP_PROJECT = "GCP_PROJECT_ID"
ENV_GOOGLE_CLOUD_PROJECT = "GOOGLE_CLOUD_PROJECT"
ENV_GEMINI_API_KEY = "GEMINI_API_KEY"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-4-hydrogen")

CASE_FILE_EXT = ".md"
CHARTE_RSE_FILENAME = "charte_rse.md"
DEFAULT_TOP_CASES = 3

USER_ROLES = {
    "consultant_public": {
        "label": "Consultant · Public Sector",
        "allowed_sectors": ["Public Sector", "Energy", "Transport"],
        "clearance": "LEVEL 2",
    },
    "manager_energie": {
        "label": "Manager · Energy & Industry",
        "allowed_sectors": ["Energy", "Industry", "Public Sector"],
        "clearance": "LEVEL 3",
    },
    "partner_finance": {
        "label": "Partner · Banking & Finance (Full Access)",
        "allowed_sectors": [
            "Banking & Finance",
            "Public Sector",
            "Energy",
            "Industry",
            "Transport",
        ],
        "clearance": "LEVEL 5 (ALL)",
    },
}

SUPABASE_THEME = {
    "bg": "#121212",
    "surface": "#242424",
    "card": "#181818",
    "border": "#2e2e2e",
    "border_input": "#393939",
    "accent": "#3ecf8e",
    "mint": "#00c573",
    "text": "#fafafa",
    "muted": "#b4b4b4",
    "smoke": "#898989",
    "danger": "#ef4444",
    "warning": "#f59e0b",
}

DLP_PATTERNS = {
    "EMAIL_ADDRESS": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "IBAN_CODE": r"\b[A-Z]{2}\d{2}(?:\s?\d{4}){4,6}\s?\d{1,3}\b",
    "PHONE_NUMBER": r"(?:\+33|0)\s?[1-9](?:[\s.-]?\d{2}){4}\b",
    "PERSON_NAME": (
        r"(?P<prefix>(?:Contact|Lead|Director|Project Manager|Signatory|Mr\.|Mrs\.|Ms\.)"
        r"\s*[:.]?\s*)(?P<pii>[A-ZÀ-Ÿ][a-zà-ÿ-]+(?:-[A-ZÀ-Ÿ][a-zà-ÿ-]+)?\s+[A-ZÀ-Ÿ][a-zà-ÿ-]+)"
    ),
}

DLP_MASK_TEMPLATE = "[{info_type}_MASKED]"
GCP_DLP_INFO_TYPES = [
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "IBAN_CODE",
    "PERSON_NAME",
    "FRANCE_NIR",
]

DOSSIER_META = [
    {
        "id": "go_nogo",
        "vol": "VOL.01",
        "code": "STRAT-01",
        "title": "Go / No-Go Analysis",
        "subtitle": "STRATEGIST ANALYST",
        "tag": "STRATEGY",
    },
    {
        "id": "cases",
        "vol": "VOL.02",
        "code": "KNOW-02",
        "title": "Sourced Client Cases",
        "subtitle": "KNOWLEDGE HUNTER",
        "tag": "CHINESE WALL",
    },
    {
        "id": "rse",
        "vol": "VOL.03",
        "code": "ESG-03",
        "title": "ESG & Low-Carbon Audit",
        "subtitle": "SUSTAINABILITY AUDITOR",
        "tag": "CSRD / GREEN IT",
    },
    {
        "id": "propale",
        "vol": "VOL.04",
        "code": "PROP-04",
        "title": "Structured Proposal",
        "subtitle": "LEAD ARCHITECT WRITER",
        "tag": "DELIVERABLE",
    },
    {
        "id": "redteam",
        "vol": "VOL.05",
        "code": "RED-05",
        "title": "Red-Team Audit",
        "subtitle": "DEVIL'S ADVOCATE",
        "tag": "COMPLIANCE",
    },
]

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "are", "was", "were",
    "have", "has", "had", "not", "but", "what", "all", "can", "will", "just",
    "should", "into", "over", "under", "between", "such", "their", "they",
    "them", "our", "your", "you", "its", "about", "which", "when", "where",
    "how", "who", "whom", "client", "project", "sector", "tender", "rfp",
}

LIVE_PROJECT_META = {
    "id": "proj_live",
    "code": "PROJ-LIVE",
    "badge": "LIVE RFP",
    "year": "2026",
    "default_title": "Uploaded Sovereign Bid",
    "default_client": "Enterprise Client",
    "default_sector": "Public Sector",
}

ANALYST_DIMENSIONS = [
    {"key": "sovereignty", "label": "Sovereignty & Security Fit", "base": 88},
    {"key": "esg", "label": "CSRD & Green IT Alignment", "base": 92},
    {"key": "delivery", "label": "Delivery & SLA Feasibility", "base": 84},
    {"key": "commercial", "label": "Commercial & FinOps Margin", "base": 80},
]

COMPLIANCE_TEMPLATE = [
    {
        "id": "REQ-01",
        "requirement": "Sovereign EU Hosting (europe-west9) & CMEK Encryption",
        "deloitte_response": "Dedicated Landing Zone in Paris europe-west9 with customer-managed keys.",
        "status": "COVERED",
        "section": "2. Sovereign Architecture",
    },
    {
        "id": "REQ-02",
        "requirement": "Automated PII Redaction (Cloud DLP) before AI Indexing",
        "deloitte_response": "Inline Cloud DLP airlock masking all citizen & banking PII upstream.",
        "status": "COVERED",
        "section": "2. Sovereign Architecture",
    },
    {
        "id": "REQ-03",
        "requirement": "CSRD Scope 2/3 Carbon Telemetry & RGESN Eco-Design",
        "deloitte_response": "Sprint-1 Carbon Footprint cockpit & frugal Gemini Flash routing.",
        "status": "COVERED",
        "section": "3. ESG & Green IT",
    },
    {
        "id": "REQ-04",
        "requirement": "SecNumCloud Attestation Matrix & Multi-Zone RPO/RTO SLA",
        "deloitte_response": "Requires explicit SecNumCloud & RPO < 15 min / RTO < 1 hr addendum.",
        "status": "PATCH_NEEDED",
        "section": "5. Risk & Governance",
    },
    {
        "id": "REQ-05",
        "requirement": "Transparent Build vs. Managed Run FinOps Pricing Cap",
        "deloitte_response": "Requires itemized Build / Run allocation table in Commercial Addendum.",
        "status": "PATCH_NEEDED",
        "section": "6. Delivery & FinOps",
    },
]

PROJECT_CATALOG = [
    {
        "id": "proj_ministry",
        "code": "BID-2026-01",
        "badge": "PORTFOLIO",
        "title": "Sovereign Data & AI Platform",
        "client": "Ministry of Ecological Transition",
        "sector": "Public Sector",
        "budget": "€1.8M",
        "deadline": "24 Months · SLA 99.95%",
        "year": "2026",
        "rfp_summary": (
            "PUBLIC SECTOR RFP — Ministry of Ecological Transition\n"
            "Subject: Sovereign Data & AI Platform Migration (42 TB) to europe-west9.\n"
            "Requirements: SecNumCloud sovereignty, CSRD Scope 2/3 tracking, Green IT RGESN, "
            "99.95% SLA (RPO < 15 min, RTO < 1 hr), €1.8M ceiling (€1.1M Build / €0.7M Run).\n"
            "Contact: Jean-Marc Delacroix | Email: jm.delacroix@transition-agency.eu | "
            "Phone: +33 6 45 82 19 30 | IBAN: FR76 3000 6000 0112 3456 7890 189"
        ),
    },
    {
        "id": "proj_eurobank",
        "code": "BID-2026-02",
        "badge": "RESTRICTED",
        "title": "Core Banking GenAI & DORA Hub",
        "client": "EuroBank Group (Tier-1)",
        "sector": "Banking & Finance",
        "budget": "€2.6M",
        "deadline": "18 Months · SLA 99.99%",
        "year": "2026",
        "rfp_summary": (
            "BANKING & FINANCE RFP — EuroBank Group (Tier-1)\n"
            "Subject: Core Banking GenAI & DORA Operational Resilience Hub.\n"
            "Requirements: ACPR & DORA compliance, Zero-Trust SecNumCloud isolation, real-time AML/KYC "
            "inference, 99.99% SLA (RPO < 5 min, RTO < 30 min), €2.6M budget, CSRD green finance reporting.\n"
            "Contact: Claire Vance-Moreau | Email: c.moreau@eurobank-group.eu | "
            "Phone: +33 1 42 68 55 10 | IBAN: FR76 1009 6000 5098 7654 3210 112"
        ),
    },
    {
        "id": "proj_grid",
        "code": "BID-2026-03",
        "badge": "PORTFOLIO",
        "title": "Smart Grid Predictive Lakehouse",
        "client": "GridFrance Energy",
        "sector": "Energy",
        "budget": "€1.4M",
        "deadline": "12 Months · SLA 99.95%",
        "year": "2026",
        "rfp_summary": (
            "ENERGY SECTOR RFP — GridFrance Energy\n"
            "Subject: Smart Grid Predictive Lakehouse for 12M smart-meter telemetry streams.\n"
            "Requirements: Hosting in europe-west9 Paris, CSRD Scope 3 grid analytics, Green IT "
            "streaming frugality, 99.95% SLA, €1.4M budget, SecNumCloud-aligned OT/IT airgap.\n"
            "Contact: Marc-Antoine Lefevre | Email: ma.lefevre@gridfrance-energy.fr | "
            "Phone: +33 6 78 90 12 34 | IBAN: FR76 2004 1000 0144 5566 7788 901"
        ),
    },
    {
        "id": "proj_rail",
        "code": "BID-2026-04",
        "badge": "PORTFOLIO",
        "title": "CSRD Fleet Decarbonization Twin",
        "client": "EuroRail Mobility",
        "sector": "Transport",
        "budget": "€980K",
        "deadline": "10 Months · SLA 99.90%",
        "year": "2026",
        "rfp_summary": (
            "TRANSPORT SECTOR RFP — EuroRail Mobility\n"
            "Subject: CSRD Fleet Decarbonization Digital Twin & Predictive Maintenance AI.\n"
            "Requirements: Low-carbon Cloud in europe-west9, automated CSRD ESRS E1 audit trails, "
            "99.90% SLA, €980K budget, GDPR/DLP masking of operator telemetry.\n"
            "Contact: Sophie Bernard-Kessler | Email: s.kessler@eurorail-mobility.eu | "
            "Phone: +33 6 11 22 33 44 | IBAN: FR76 3000 4000 0299 8877 6655 432"
        ),
    },
]
