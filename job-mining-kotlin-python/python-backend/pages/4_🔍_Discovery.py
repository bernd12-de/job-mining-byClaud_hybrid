"""
🔍 Discovery - Neue Skills Management
Discovery Learning System
"""
import requests
import streamlit as st
import pandas as pd

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DiscoveryPage")

# API ENDPOINTS
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

st.set_page_config(page_title="Discovery | Job Mining", page_icon="🔍", layout="wide")

@st.cache_data(ttl=300)
def fetch_discovery_candidates():
    """Lädt Discovery Candidates von Kotlin API"""
    try:
        response = requests.get(f"{KOTLIN_API_BASE}/api/discovery/candidates", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # API gibt Liste von Strings oder Dictionaries zurück
            if isinstance(data, list):
                if data and isinstance(data[0], str):
                    # Konvertiere String-Liste zu Dictionary-Liste
                    return [{'text': item, 'entity_type': 'skill', 'count': 1} for item in data]
                return data
            return []
        return []
    except Exception as e:
        logger.error(f"Fehler beim Laden der Discovery Candidates: {e}")
        return []


def approve_candidate(entity_id):
    try:
        response = requests.post(f"{PYTHON_API_BASE}/discovery/approve/{entity_id}", timeout=5)
        return response.status_code == 200
    except:
        return False

def ignore_candidate(entity_id):
    try:
        response = requests.post(f"{PYTHON_API_BASE}/discovery/ignore/{entity_id}", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    st.title("🔍 Discovery: Neue Skills Management")
    st.caption("Selbstlernendes System für automatische Skill-Erkennung")


    # Lade Candidates
    with st.spinner("Analysiere neue Skills..."):
        candidates = fetch_discovery_candidates()

    if not candidates:
        st.warning("⚠️ Keine Discovery Candidates gefunden. Bitte analysiere zuerst Jobs.")
        st.info(f"API Endpoint: {KOTLIN_API_BASE}/api/discovery/candidates")
        return

    # Filtere nach Typ (falls vorhanden)
    skills = [c for c in candidates if c.get('entity_type') == 'skill']
    tools = [c for c in candidates if c.get('entity_type') == 'tool']

    #candidates = fetch_discovery_candidates()
    skills = [c for c in candidates if c.get('entity_type') == 'skill']
    pending = [c for c in candidates if c.get('status') == 'pending']



    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🆕 Neue Skills", len(skills))
    with col2:
        st.metric("⏳ Pending", len(pending))
    with col3:
        st.metric("✅ Auto-Promoted", len([c for c in candidates if c.get('level', 0) >= 2]))
    with col4:
        st.metric("📈 Gesamt", len(candidates))

    st.markdown("---")

    # Tabs
    tab1, tab2 = st.tabs(["📋 Candidates", "📊 Statistik"])

    with tab1:
        st.markdown("### 🆕 Discovery Candidates")

        if not candidates:
            st.info("Keine Candidates gefunden. Starten Sie eine Job-Analyse.")
        else:
            # Filter
            filter_type = st.selectbox("Filter:", ["Alle", "Skills", "Rollen", "Industrien"])

            filtered = candidates
            if filter_type == "Skills":
                filtered = [c for c in candidates if c.get('entity_type') == 'skill']
            elif filter_type == "Rollen":
                filtered = [c for c in candidates if c.get('entity_type') == 'role']
            elif filter_type == "Industrien":
                filtered = [c for c in candidates if c.get('entity_type') == 'industry']

            # Tabelle
            for candidate in filtered[:20]:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 2])

                with col1:
                    st.markdown(f"**{candidate.get('text', 'N/A')}**")
                    st.caption(f"{candidate.get('entity_type', 'N/A')} | Level {candidate.get('level', 1)}")

                with col2:
                    st.metric("Häufigkeit", candidate.get('occurrences', 0))

                with col3:
                    st.metric("Confidence", f"{candidate.get('confidence', 0):.0%}")

                with col4:
                    if st.button("✅ Approve", key=f"approve_{candidate.get('id')}"):
                        if approve_candidate(candidate.get('id')):
                            st.success("Approved!")
                            st.rerun()

                    if st.button("🚫 Ignore", key=f"ignore_{candidate.get('id')}"):
                        if ignore_candidate(candidate.get('id')):
                            st.success("Ignored!")
                            st.rerun()

                st.markdown("---")

    with tab2:
        st.markdown("### 📊 Discovery Statistik")

        if candidates:
            df = pd.DataFrame([
                {'Type': 'Skills', 'Anzahl': len([c for c in candidates if c.get('entity_type') == 'skill'])},
                {'Type': 'Rollen', 'Anzahl': len([c for c in candidates if c.get('entity_type') == 'role'])},
                {'Type': 'Industrien', 'Anzahl': len([c for c in candidates if c.get('entity_type') == 'industry'])},
            ])

            st.bar_chart(df.set_index('Type'))

            # Level-Verteilung
            level_dist = {}
            for c in candidates:
                level = c.get('level', 1)
                level_dist[level] = level_dist.get(level, 0) + 1

            st.markdown("### Level-Verteilung")
            st.bar_chart(level_dist)
        else:
            st.info("Keine Daten vorhanden.")

if __name__ == "__main__":
    main()
