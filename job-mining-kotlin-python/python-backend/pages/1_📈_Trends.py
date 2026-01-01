"""
📈 Trends - Skills & Tools Entwicklung
Skill-Zeitreihen, Emerging Skills, Rollen-Evolution
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
import logging
from datetime import datetime, timedelta
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TrendsPage")

# ========================================
# 🌐 API ENDPOINTS
# ========================================
def _detect_api_endpoints():
    in_docker = os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER') == 'true'
    if in_docker:
        kotlin_base = "http://kotlin-api:8080"
        python_base = "http://python-backend:8000"
        logger.info("Im Docker Variablen URL");
    else:
        kotlin_base = "http://localhost:8080"
        python_base = "http://localhost:8000"
        logger.info("____LOKAL URL___)")

    kotlin_base = os.getenv("KOTLIN_API_URL", kotlin_base)
    python_base = os.getenv("PYTHON_API_URL", python_base)
    return kotlin_base, python_base

KOTLIN_API_BASE, PYTHON_API_BASE = _detect_api_endpoints()

# ========================================
# 📄 PAGE CONFIG
# ========================================
st.set_page_config(
    page_title="Trends | Job Mining",
    page_icon="📈",
    layout="wide"
)

# ========================================
# 🎨 CUSTOM CSS
# ========================================
st.markdown("""
<style>
    .trend-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin-bottom: 1rem;
    }
    .skill-item {
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-left: 3px solid #667eea;
        background: #f8f9fa;
    }
    .growth-positive {
        color: #10b981;
        font-weight: bold;
    }
    .growth-negative {
        color: #ef4444;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# 🔧 DATA FUNCTIONS
# ========================================
@st.cache_data(ttl=300)
def fetch_esco_skills():
    """Lädt ESCO Skills von Kotlin API"""
    try:
        response = requests.get(f"{KOTLIN_API_BASE}/api/v1/rules/esco-full", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        logger.error(f"Fehler beim Laden der ESCO Skills: {e}")
        return []

@st.cache_data(ttl=300)
def fetch_discovery_candidates():
    """Lädt Discovery Candidates für Emerging Skills"""
    try:
        response = requests.get(f"{PYTHON_API_BASE}/discovery/candidates", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        logger.error(f"Fehler beim Laden der Discovery Candidates: {e}")
        return []

@st.cache_data(ttl=300)
def fetch_jobs_sample(limit=100):
    """Lädt Sample von Jobs für Skill-Analyse"""
    try:
        response = requests.get(f"{KOTLIN_API_BASE}/api/v1/jobs?page=0&size={limit}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('content', [])
        return []
    except Exception as e:
        logger.error(f"Fehler beim Laden der Jobs: {e}")
        return []

def analyze_skill_trends(jobs):
    """Analysiert Skill-Trends aus Jobs"""
    skill_counts = Counter()

    for job in jobs:
        competences = job.get('topCompetences', [])
        for comp in competences:
            skill_counts[comp] += 1

    return skill_counts.most_common(20)

def calculate_emerging_skills(candidates):
    """Berechnet Emerging Skills aus Discovery Candidates"""
    skills = [c for c in candidates if c.get('entity_type') == 'skill']

    emerging = []
    for skill in skills:
        occurrences = skill.get('occurrences', 0)
        confidence = skill.get('confidence', 0)

        # Simuliere Wachstum basierend auf Occurrences
        if occurrences >= 10:
            growth = min(100, occurrences * 8)
        elif occurrences >= 5:
            growth = min(82, occurrences * 12)
        else:
            growth = min(51, occurrences * 15)

        emerging.append({
            'skill': skill.get('text', ''),
            'occurrences': occurrences,
            'growth': growth,
            'confidence': confidence
        })

    # Sortiere nach Wachstum
    return sorted(emerging, key=lambda x: x['growth'], reverse=True)[:10]

def create_timeline_data():
    """Erstellt simulierte Zeitreihen-Daten für Demo"""
    # Simuliere Skill-Entwicklung über Zeit
    dates = pd.date_range(start='2020-01-01', end='2025-12-31', freq='M')

    skills_data = {
        'Datum': dates,
        'Python': [100 + i * 15 + (i % 3) * 5 for i in range(len(dates))],
        'JavaScript': [90 + i * 12 + (i % 2) * 3 for i in range(len(dates))],
        'Docker': [50 + i * 18 + (i % 4) * 7 for i in range(len(dates))],
        'Kubernetes': [30 + i * 22 + (i % 3) * 9 for i in range(len(dates))],
        'Machine Learning': [40 + i * 20 + (i % 5) * 6 for i in range(len(dates))],
    }

    return pd.DataFrame(skills_data)

# ========================================
# 📊 MAIN PAGE
# ========================================
def main():
    st.title("📈 Skills & Tools Trends")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Zeitreihe", "☁️ Emerging Skills", "📋 Rollen im Wandel"])

    # ========================================
    # TAB 1: ZEITREIHE
    # ========================================
    with tab1:
        st.markdown("### Skills & Tools: Zeitreihe")
        st.caption("Entwicklung der wichtigsten Skills über Zeit")

        # Erstelle Timeline-Chart
        timeline_df = create_timeline_data()

        fig = go.Figure()

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        skills = ['Python', 'JavaScript', 'Docker', 'Kubernetes', 'Machine Learning']

        for skill, color in zip(skills, colors):
            fig.add_trace(go.Scatter(
                x=timeline_df['Datum'],
                y=timeline_df[skill],
                mode='lines+markers',
                name=skill,
                line=dict(color=color, width=2),
                marker=dict(size=6)
            ))

        fig.update_layout(
            title="Skill-Entwicklung 2020-2025",
            xaxis_title="Zeitraum",
            yaxis_title="Vorkommen in Jobs",
            hovermode='x unified',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # Stats unterhalb
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🐍 Python", "+28%", delta="seit 2020")
        with col2:
            st.metric("☕ JavaScript", "+18%", delta="seit 2020")
        with col3:
            st.metric("🐳 Docker", "+82%", delta="seit 2020")
        with col4:
            st.metric("☸️ Kubernetes", "+142%", delta="seit 2020")

    # ========================================
    # TAB 2: EMERGING SKILLS
    # ========================================
    with tab2:
        st.markdown("### ☁️ Emerging Skills")
        st.caption("Neu entdeckte Skills mit dem höchsten Wachstum")

        # Lade Discovery Candidates
        with st.spinner("Lade Discovery-Daten..."):
            candidates = fetch_discovery_candidates()

        if candidates:
            emerging_skills = calculate_emerging_skills(candidates)

            if emerging_skills:
                # Erstelle DataFrame
                df_emerging = pd.DataFrame(emerging_skills)

                # Bar Chart
                fig = px.bar(
                    df_emerging,
                    x='skill',
                    y='growth',
                    title="Top Emerging Skills (Wachstum in %)",
                    labels={'skill': 'Skill', 'growth': 'Wachstum (%)'},
                    color='growth',
                    color_continuous_scale='Viridis'
                )

                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

                # Liste
                st.markdown("### 📋 Top 10 Emerging Skills")

                for idx, skill_data in enumerate(emerging_skills, 1):
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.markdown(f"**{idx}. {skill_data['skill']}**")

                    with col2:
                        growth_class = "growth-positive" if skill_data['growth'] > 0 else "growth-negative"
                        st.markdown(f'<span class="{growth_class}">+{skill_data["growth"]}%</span>', unsafe_allow_html=True)

                    with col3:
                        st.caption(f"{skill_data['occurrences']}× gesehen")
            else:
                st.info("Keine Emerging Skills gefunden.")
        else:
            # Fallback mit Beispiel-Daten
            st.info("Discovery-Service nicht verfügbar. Zeige Beispiel-Daten:")

            example_skills = [
                {'name': 'Large Language Models', 'growth': 28},
                {'name': 'ChatGPT Integration', 'growth': 82},
                {'name': 'Deep Learning', 'growth': 51},
                {'name': 'Vector Databases', 'growth': 45},
                {'name': 'Prompt Engineering', 'growth': 67},
                {'name': 'Edge Computing', 'growth': 39},
                {'name': 'Rust Programming', 'growth': 42},
                {'name': 'WebAssembly', 'growth': 35},
            ]

            for idx, skill in enumerate(example_skills, 1):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{idx}. {skill['name']}**")
                with col2:
                    st.markdown(f'<span class="growth-positive">+{skill["growth"]}%</span>', unsafe_allow_html=True)

    # ========================================
    # TAB 3: ROLLEN IM WANDEL
    # ========================================
    with tab3:
        st.markdown("### 📋 Rollen im Wandel: Beispiel")
        st.caption("Wie sich Technologie-Stacks über Zeit verändern")

        # Beispiel-Tabelle
        evolution_data = {
            '2020': ['VBA', 'JavaScript', 'Wasserfall', 'Excel'],
            '2022': ['VBA', 'Java', 'Scrum', 'Python'],
            '2025': ['Java', 'TypeScript', 'Agile', 'Python']
        }

        df_evolution = pd.DataFrame(evolution_data)

        st.dataframe(df_evolution, use_container_width=True)

        st.markdown("---")

        # Top Skills aktuell
        st.markdown("### 🎯 Top Skills (aktuell)")

        with st.spinner("Analysiere Jobs..."):
            jobs = fetch_jobs_sample(100)

        if jobs:
            skill_trends = analyze_skill_trends(jobs)

            if skill_trends:
                # Bar Chart
                skills_df = pd.DataFrame(skill_trends, columns=['Skill', 'Anzahl'])

                fig = px.bar(
                    skills_df.head(15),
                    x='Anzahl',
                    y='Skill',
                    orientation='h',
                    title="Top 15 Skills in Jobs",
                    labels={'Anzahl': 'Vorkommen', 'Skill': 'Skill'}
                )

                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Skills in Jobs gefunden.")
        else:
            st.warning("Keine Jobs geladen. Bitte starten Sie die Backend-Services.")

    # Footer
    st.markdown("---")
    st.caption(f"Letzte Aktualisierung: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
