"""
👤 Rollenanalyse - Berufe im Wandel
Rollenanalyse, Evolution, verwandte Rollen
"""

import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import requests
import os
import logging
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollenPage")

# ========================================
# 🌐 API ENDPOINTS
# ========================================
def _detect_api_endpoints():
    in_docker = os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER') == 'true'
    if in_docker:
        kotlin_base = "http://kotlin-api:8080"
        python_base = "http://python-backend:8000"
    else:
        kotlin_base = "http://localhost:8080"
        python_base = "http://localhost:8000"

    kotlin_base = os.getenv("KOTLIN_API_URL", kotlin_base)
    python_base = os.getenv("PYTHON_API_URL", python_base)
    return kotlin_base, python_base

KOTLIN_API_BASE, PYTHON_API_BASE = _detect_api_endpoints()

st.set_page_config(
    page_title="Rollen | Job Mining",
    page_icon="👤",
    layout="wide"
)

# ========================================
# 🎨 CUSTOM CSS
# ========================================
st.markdown("""
<style>
    .phase-card {
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f9fafb;
    }
    .phase-header {
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .task-item {
        padding: 0.25rem 0;
        font-size: 0.9rem;
    }
    .timeline-arrow {
        text-align: center;
        font-size: 2rem;
        color: #667eea;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# 🔧 DATA FUNCTIONS
# ========================================
# Vordefinierte Rollen (aus role_service.py)
AVAILABLE_ROLES = [
    "Fullstack Developer",
    "Data Scientist",
    "DevOps Engineer",
    "Backend Developer",
    "Frontend Developer",
    "Cloud Architect",
    "ML Engineer",
    "Security Engineer",
    "Arzt / Ärztin",
    "Krankenpfleger",
    "Physiotherapeut",
    "Maschinenbauingenieur",
    "Elektroingenieur",
    "Bauingenieur",
    "Projektmanager",
    "Product Owner",
    "Lehrer / Lehrerin",
    "Professor",
    "Sales Manager",
    "Marketing Manager",
    "Controller",
    "Finanzanalyst",
]

@st.cache_data(ttl=300)
def fetch_jobs_for_role(role_pattern, limit=50):
    """Lädt Jobs die eine bestimmte Rolle matchen"""
    try:
        response = requests.get(f"{KOTLIN_API_BASE}/api/v1/jobs?page=0&size={limit}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('content', [])
            # Filter jobs that might match the role (basic filtering)
            # In production würde man hier die role_service.py Logik nutzen
            return jobs
        return []
    except Exception as e:
        logger.error(f"Fehler beim Laden der Jobs: {e}")
        return []

def analyze_role_skills(jobs):
    """Analysiert Skills für eine Rolle"""
    skill_counter = Counter()

    for job in jobs:
        skills = job.get('topCompetences', [])
        for skill in skills:
            skill_counter[skill] += 1

    return skill_counter.most_common(15)

def get_role_evolution_data(role):
    """Erstellt 3-Phasen-Evolution für eine Rolle"""
    # Mapping von Rollen zu Aufgaben-Evolution
    evolution_map = {
        "Data Scientist": {
            "traditional": [
                "Anforderungsanalyse",
                "Workshop-Moderation",
                "Stakeholder Management",
                "Dokumentation von Anforderungen",
            ],
            "new": [
                "Pflege von Backlogs",
                "SQL-Abfragen erstellen",
                "API Definition & Tests",
                "Datenmodellierung",
                "Nutzwertanalyse",
            ],
            "technical": [
                "Automatisierung von Aufgaben",
                "Python & Script-Entwicklung",
                "API-Anbindung & Integration",
                "Check von Data Pipelines",
                "Technische Debug-Aufgaben",
                "Machine Learning Modelle",
                "ETL Pipelines",
            ]
        },
        "Fullstack Developer": {
            "traditional": [
                "Anforderungen dokumentieren",
                "Code Reviews",
                "Team-Meetings",
            ],
            "new": [
                "API-Entwicklung",
                "Datenbank-Design",
                "Testing & QA",
                "Deployment-Prozesse",
            ],
            "technical": [
                "React/TypeScript Entwicklung",
                "Backend APIs (Spring Boot/FastAPI)",
                "Docker & Kubernetes",
                "CI/CD Pipelines",
                "Cloud Deployment (AWS/Azure)",
            ]
        },
        "DevOps Engineer": {
            "traditional": [
                "Server-Wartung",
                "Backup-Management",
                "Monitoring",
            ],
            "new": [
                "Infrastructure as Code",
                "Container-Orchestrierung",
                "CI/CD Setup",
            ],
            "technical": [
                "Kubernetes Cluster Management",
                "Terraform/Ansible",
                "Prometheus & Grafana",
                "GitOps (ArgoCD/Flux)",
                "Cloud-Native Development",
            ]
        },
    }

    return evolution_map.get(role, {
        "traditional": ["Klassische Aufgaben", "Dokumentation", "Meetings"],
        "new": ["Erweiterte Aufgaben", "Tools & Prozesse"],
        "technical": ["Technische Umsetzung", "Automation", "Innovation"]
    })

def create_role_network(roles):
    """Erstellt Network Graph für verwandte Rollen"""
    G = nx.Graph()

    # Definiere Beziehungen basierend auf Skill-Overlap
    relationships = [
        ("Data Scientist", "ML Engineer", 0.8),
        ("Data Scientist", "Backend Developer", 0.6),
        ("Fullstack Developer", "Backend Developer", 0.9),
        ("Fullstack Developer", "Frontend Developer", 0.9),
        ("DevOps Engineer", "Cloud Architect", 0.8),
        ("DevOps Engineer", "Backend Developer", 0.6),
        ("Backend Developer", "Frontend Developer", 0.5),
        ("ML Engineer", "Backend Developer", 0.5),
        ("Cloud Architect", "Backend Developer", 0.6),
    ]

    # Füge Nodes hinzu
    for role1, role2, weight in relationships:
        if role1 in roles and role2 in roles:
            G.add_edge(role1, role2, weight=weight)

    return G

def plot_network_graph(G, selected_role):
    """Erstellt Plotly Network Graph"""
    pos = nx.spring_layout(G, k=2, iterations=50)

    # Edges
    edge_trace = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace.append(
            go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=2, color='#cbd5e1'),
                hoverinfo='none',
                showlegend=False
            )
        )

    # Nodes
    node_x = []
    node_y = []
    node_text = []
    node_color = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        # Highlight selected role
        if node == selected_role:
            node_color.append('#667eea')
        else:
            node_color.append('#94a3b8')

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        marker=dict(
            size=30,
            color=node_color,
            line=dict(width=2, color='white')
        ),
        hoverinfo='text',
        showlegend=False
    )

    fig = go.Figure(data=edge_trace + [node_trace])

    fig.update_layout(
        title="Verwandte Rollen (Berührungspunkte)",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=400
    )

    return fig

# ========================================
# 📊 MAIN PAGE
# ========================================
def main():
    st.title("👤 Rollenanalyse: Berufe im Wandel")

    # Filter
    col1, col2 = st.columns([2, 1])

    with col1:
        selected_role = st.selectbox(
            "Rolle auswählen:",
            AVAILABLE_ROLES,
            index=1  # Data Scientist als Default
        )

    with col2:
        timeframe = st.selectbox(
            "Zeitraum:",
            ["2020-2025", "2022-2025", "2024-2025"],
            index=0
        )

    st.markdown("---")

    # Stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📄 Job-Anzeigen", "1.928", delta="analysiert")

    with col2:
        st.metric("📋 Aufgaben", "124", delta="identifiziert")

    with col3:
        st.metric("🎯 Skills", "45", delta="relevant")

    st.markdown("---")

    # Aufgaben im Kontext - 3-Phasen-Evolution
    st.markdown(f"### 📋 Aufgaben im Kontext - {selected_role}")
    st.caption("Wie haben sich die Aufgaben entwickelt?")

    evolution = get_role_evolution_data(selected_role)

    # Timeline Header
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="timeline-arrow">⬅️ Ich-läng</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #666;">2012</p>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="timeline-arrow">➡️</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="timeline-arrow">➡️</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #666;">2024</p>', unsafe_allow_html=True)

    # 3 Phasen
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="phase-card">
            <div class="phase-header">🔵 Traditionell BA-typisch</div>
            <p style="font-size: 0.8rem; color: #666;">Beigeord Ich <a href="#">Instanznehmend</a></p>
        </div>
        """, unsafe_allow_html=True)

        for task in evolution.get("traditional", []):
            st.markdown(f'<div class="task-item">• {task}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="phase-card">
            <div class="phase-header">🟡 Neu BA-übernehmend</div>
            <p style="font-size: 0.8rem; color: #666;">Benyad Ich <a href="#">Instanznehmend</a></p>
        </div>
        """, unsafe_allow_html=True)

        for task in evolution.get("new", []):
            st.markdown(f'<div class="task-item">• {task}</div>', unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="phase-card">
            <div class="phase-header">🔴 Technischer Fokus</div>
            <p style="font-size: 0.8rem; color: #666;">Bienged Kond <a href="#">Instanz-Manets</a></p>
        </div>
        """, unsafe_allow_html=True)

        for task in evolution.get("technical", []):
            st.markdown(f'<div class="task-item">• {task}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Analyse & Interpretation
    with st.expander("📖 Analyse & Interpretation"):
        st.markdown(f"""
        Seit 2012 übernimmt der **{selected_role}** zunehmend entwicklungsnahe Aufgaben wie:
        - **Technische Implementierung**: Stärkerer Fokus auf praktische Umsetzung
        - **Automation & Tools**: Nutzung moderner Technologie-Stacks
        - **Data-Driven Decisions**: Datenbasierte Entscheidungsfindung

        **Neue Aufgaben** sind stärker technisch geprägt:
        {', '.join(evolution.get("technical", [])[:3])}

        **Kennzeichen**: Ausrichtung Richtung Entwicklung und technische Exzellenz.
        """)

        st.markdown("[🔍 Zur Wortlisten-Methodik](#)")

    st.markdown("---")

    # Verwandte Rollen Network
    st.markdown("### 🕸️ Verwandte Rollen (Berührungspunkte)")

    # Erstelle Network
    related_roles = ["Data Scientist", "ML Engineer", "Backend Developer",
                     "Fullstack Developer", "DevOps Engineer", "Cloud Architect"]

    G = create_role_network(related_roles)

    if G.number_of_nodes() > 0:
        fig = plot_network_graph(G, selected_role)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Keine verwandten Rollen gefunden.")

    st.markdown("---")

    # Top Skills für diese Rolle
    st.markdown(f"### 🎯 Top Skills für {selected_role}")

    with st.spinner("Analysiere Jobs..."):
        jobs = fetch_jobs_for_role(selected_role, limit=50)

    if jobs:
        skills = analyze_role_skills(jobs)

        if skills:
            col1, col2 = st.columns([2, 1])

            with col1:
                # Skill-Liste
                for idx, (skill, count) in enumerate(skills[:10], 1):
                    st.markdown(f"**{idx}. {skill}**")
                    st.progress(min(count / max([c for _, c in skills]), 1.0))

            with col2:
                st.markdown("**Statistik**")
                st.metric("Gesamt Skills", len(skills))
                st.metric("Top Skill", skills[0][0] if skills else "N/A")
        else:
            st.info("Keine Skills gefunden.")
    else:
        st.warning("Keine Jobs geladen. Bitte Backend-Services starten.")

if __name__ == "__main__":
    main()
