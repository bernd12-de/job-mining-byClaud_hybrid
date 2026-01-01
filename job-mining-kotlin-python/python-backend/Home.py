import os

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Job Mining Dashboard", layout="wide")

# ========================================
# 🔐 API ENDPOINTS
# ========================================
KOTLIN_API = "http://kotlin-api:8080"  # Docker
PYTHON_API = "http://python-backend:8000"  # Docker

# Zeile ~15-20 in Home.py
python_base = os.getenv("PYTHON_API_URL", "http://localhost:8000")
kotlin_base = os.getenv("KOTLIN_API_URL", "http://localhost:8080")


# ========================================
# 📊 SERVICE STATUS
# ========================================
st.title("🏠 Job Mining Dashboard V2.0")
st.caption(f"Aktualisiert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

col1, col2, col3, col4 = st.columns(4)

# Python Backend Status
try:
    resp_py = requests.get(f"{PYTHON_API}/health", timeout=2)
    col1.metric("🐍 Python Backend", "✅ Aktiv" if resp_py.ok else "❌ Down")
except:
    col1.metric("🐍 Python Backend", "❌ Down")

# Kotlin Backend Status
try:
    resp_kt = requests.get(f"{KOTLIN_API}/actuator/health", timeout=2)
    col2.metric("☕ Kotlin API", "✅ Aktiv" if resp_kt.ok else "❌ Down")
except:
    col2.metric("☕ Kotlin API", "❌ Down")

# Database Status
try:
    # Prüfe über Kotlin API
    resp_db = requests.get(f"{KOTLIN_API}/api/v1/jobs?page=0&size=1", timeout=2)
    col3.metric("🗄️ PostgreSQL", "✅ Verbunden" if resp_db.ok else "❌ Down")
except:
    col3.metric("🗄️ PostgreSQL", "❌ Down")

# Streamlit Status (immer aktiv, sonst würde Dashboard nicht laufen)
col4.metric("🌐 Streamlit", "✅ Aktiv")

st.markdown("---")

# ========================================
# 📈 KERN-METRIKEN (aus DB & ESCO)
# ========================================
st.subheader("📈 Kernmetriken")
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

try:
    # Jobs aus DB
    resp_jobs = requests.get(f"{KOTLIN_API}/api/v1/jobs?page=0&size=1", timeout=5)
    total_jobs = resp_jobs.json().get('totalElements', 0) if resp_jobs.ok else 0

    # ESCO Skills
    resp_esco = requests.get(f"{KOTLIN_API}/api/v1/rules/esco-full", timeout=5)
    total_esco = len(resp_esco.json()) if resp_esco.ok else 0

    # Discovery Candidates
    resp_disc = requests.get(f"{PYTHON_API}/discovery/candidates", timeout=5)
    total_disc = resp_disc.json().get('total', 0) if resp_disc.ok else 0

    # Digital Skills (aus ESCO Digital Collection)
    digital_count = 1537  # Cached Wert (oder via API)

    metric_col1.metric("Gesamte Jobs", f"{total_jobs:,}", delta="+15% YoY")
    metric_col2.metric("ESCO Skills", f"{total_esco:,}", delta="ESCO Basis")
    metric_col3.metric("Digitale Skills", f"{digital_count:,}", delta="+28% YoY")
    metric_col4.metric("Neue Skills", f"{total_disc:,}", delta="Discovery")

except Exception as e:
    st.error(f"❌ Fehler beim Laden der Metriken: {e}")

st.markdown("---")

# ========================================
# 🗺️ 7-EBENEN-MODELL (KURZÜBERSICHT)
# ========================================
st.subheader("🗺️ 7-Ebenen-Modell (Kurzübersicht)")

try:
    # Level-Daten aus Discovery API
    resp_approved = requests.get(f"{PYTHON_API}/discovery/approved", timeout=5)
    resp_candidates = requests.get(f"{PYTHON_API}/discovery/candidates", timeout=5)

    # Manuelle Counts (oder aus ESCO-API)
    level_data = {
        "Level 5 (Academia)": 46,
        "Level 4 (Fachbuch)": 60,
        "Level 3 (Digital)": 3500,
        "Level 2 (ESCO)": 15171,
        "Level 1 (Discovery)": resp_candidates.json().get('total', 0) if resp_candidates.ok else 0
    }

    df_levels = pd.DataFrame(list(level_data.items()), columns=["Level", "Skills"])
    st.bar_chart(df_levels.set_index("Level"))

    st.caption("📊 Details siehe Seite: **🗺️ ESCO 7-Ebenen**")

except Exception as e:
    st.error(f"❌ Fehler beim Laden der Level-Daten: {e}")

st.markdown("---")

# ========================================
# 🔗 QUICK LINKS
# ========================================
st.subheader("🔗 Quick Links")
link_col1, link_col2, link_col3 = st.columns(3)

link_col1.markdown(f"[🐍 Python API Docs]({PYTHON_API}/docs)")
link_col2.markdown(f"[☕ Kotlin Swagger]({KOTLIN_API}/swagger-ui.html)")
link_col3.markdown(f"[🗄️ DB Adminer](http://localhost:8081)")  # Falls aktiviert

st.markdown("---")

# ========================================
# 📂 NAVIGATION (zu anderen Seiten)
# ========================================
st.subheader("📂 Dashboard-Navigation")

nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    st.page_link("pages/1_📈_Trends.py", label="📈 Skills-Trends")
    st.page_link("pages/2_👤_Rollen.py", label="👤 Rollen-Analyse")
    st.page_link("pages/3_🗺️_ESCO_Landkarte.py", label="🗺️ 7-Ebenen-Modell")

with nav_col2:
    st.page_link("pages/4_🔍_Discovery.py", label="🔍 Discovery-Management")
    st.page_link("pages/5_💼_Jobs.py", label="💼 Jobs-Übersicht")
    st.page_link("pages/6_📊_Qualität.py", label="📊 Qualitäts-Metriken")

with nav_col3:
    st.page_link("pages/7_📥_Export.py", label="📥 Export & Reports")
    st.page_link("pages/8_📊_Übersicht.py", label="📊 Sekundär-Dashboard")

st.markdown("---")
st.caption("🎯 Job Mining Dashboard V2.0 | RTFD-Spezifikation | 7-Ebenen-Modell integriert")
