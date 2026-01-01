"""
💼 Jobs - Job-Übersicht & Details
Integration des Original-Dashboards
"""

import streamlit as st
import pandas as pd
import requests
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JobsPage")

def _detect_api_endpoints():
    in_docker = os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER') == 'true'
    if in_docker:
        kotlin_base = "http://kotlin-api:8080"
        python_base = "http://python-backend:8000"
    else:
        kotlin_base = "http://localhost:8080"
        python_base = "http://localhost:8000"

    return os.getenv("KOTLIN_API_URL", kotlin_base), os.getenv("PYTHON_API_URL", python_base)

KOTLIN_API_BASE, PYTHON_API_BASE = _detect_api_endpoints()

st.set_page_config(page_title="Jobs | Job Mining", page_icon="💼", layout="wide")

@st.cache_data(ttl=300)
def fetch_jobs(page=0, size=20):
    try:
        response = requests.get(f"{KOTLIN_API_BASE}/api/v1/jobs?page={page}&size={size}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Fehler: {e}")
        return None

def main():
    st.title("💼 Jobs-Übersicht")
    st.caption("Analysierte Stellenanzeigen")

    # Pagination
    page = st.number_input("Seite:", min_value=0, value=0, step=1)
    size = st.selectbox("Pro Seite:", [10, 20, 50, 100], index=1)

    # Lade Jobs
    with st.spinner("Lade Jobs..."):
        data = fetch_jobs(page, size)

    if data:
        jobs = data.get('content', [])
        total = data.get('totalElements', 0)

        st.success(f"✅ {total:,} Jobs gesamt | Seite {page + 1} von {data.get('totalPages', 1)}")

        # Jobs-Tabelle
        if jobs:
            for idx, job in enumerate(jobs, start=page * size + 1):
                with st.expander(f"#{idx} - {job.get('title', 'N/A')}"):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"**Unternehmen:** {job.get('company', 'N/A')}")
                        st.markdown(f"**Ort:** {job.get('location', 'N/A')}")
                        st.markdown(f"**ID:** {job.get('id', 'N/A')}")

                    with col2:
                        st.metric("Skills", len(job.get('topCompetences', [])))
                        st.metric("Quelle", job.get('source', 'N/A'))

                    # Top Skills
                    st.markdown("**Top Skills:**")
                    skills = job.get('topCompetences', [])[:10]
                    if skills:
                        st.write(", ".join(skills))
                    else:
                        st.caption("Keine Skills gefunden")

        # Export
        st.markdown("---")
        if st.button("📥 Export CSV"):
            df = pd.DataFrame(jobs)
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, "jobs.csv", "text/csv")
    else:
        st.error("❌ Konnte Jobs nicht laden. Bitte Backend-Services starten.")
        st.info(f"Kotlin API: {KOTLIN_API_BASE}/api/v1/jobs")

if __name__ == "__main__":
    main()
