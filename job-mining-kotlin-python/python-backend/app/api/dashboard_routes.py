"""
Dashboard API mit echten Datenbank-Daten
"""
from fastapi import APIRouter, HTTPException
from sqlalchemy import func, text
from app.infrastructure.database import SessionLocal
from app.infrastructure.db_models import Job, Skill, DiscoveryCandidate
from typing import Dict, Any
import logging

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
logger = logging.getLogger(__name__)


@router.get("/stats")
async def get_dashboard_stats() -> Dict[str, Any]:
    """
    📊 Dashboard-Haupt-Statistiken (echte DB-Daten)

    Returns:
        - total_jobs: Anzahl Jobs
        - total_skills: Anzahl ESCO Skills
        - discovery_skills: Neue entdeckte Skills
        - avg_quality: Durchschnittliche Extraktionsqualität
    """
    try:
        db = SessionLocal()

        # Jobs zählen
        total_jobs = db.query(func.count(Job.id)).scalar()

        # Unique Skills (ESCO-Codes)
        total_skills = db.query(func.count(func.distinct(Skill.esco_code))).scalar()

        # Discovery Skills (neue Kandidaten)
        discovery_skills = db.query(func.count(DiscoveryCandidate.id)).scalar()

        # Durchschnittliche Qualität (aus Jobs)
        avg_quality = db.query(func.avg(Job.extraction_quality)).scalar() or 0.0

        db.close()

        return {
            "total_jobs": total_jobs,
            "total_skills": total_skills,
            "discovery_skills": discovery_skills,
            "avg_quality": round(avg_quality * 100, 1),  # 87.5%
            "years_covered": [2020, 2021, 2022, 2023, 2024, 2025]
        }

    except Exception as e:
        logger.error(f"Fehler beim Laden der Dashboard-Stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/competence-trends")
async def get_competence_trends() -> Dict[str, Any]:
    """
    📈 Skill-Trends über Zeit (Chart.js Format)

    Gruppiert Jobs nach Jahr und zählt Top Skills.
    """
    try:
        db = SessionLocal()

        # SQL-Query: Skills pro Jahr zählen
        query = text("""
                     SELECT
                         EXTRACT(YEAR FROM j.posting_date) AS year,
                s.label,
                COUNT(*) AS count
                     FROM jobs j
                         JOIN skills s ON s.job_id = j.id
                     WHERE j.posting_date IS NOT NULL
                     GROUP BY year, s.label
                     ORDER BY year, count DESC;
                     """)

        result = db.execute(query).fetchall()
        db.close()

        # Transformiere zu Chart.js Format
        labels = sorted(set(row[0] for row in result))
        datasets = {}

        for year, label, count in result:
            if label not in datasets:
                datasets[label] = {
                    "label": label,
                    "data": [0] * len(labels),
                    "borderColor": get_random_color(),
                    "tension": 0.4
                }

            year_index = labels.index(year)
            datasets[label]["data"][year_index] = count

        # Top 5 Skills
        top_datasets = list(datasets.values())[:5]

        return {
            "labels": [str(int(y)) for y in labels],
            "datasets": top_datasets
        }

    except Exception as e:
        logger.error(f"Fehler beim Laden der Trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_random_color() -> str:
    """Generiert zufällige Chart.js Farben"""
    import random
    colors = [
        '#3498db', '#e74c3c', '#2ecc71', '#f39c12',
        '#9b59b6', '#1abc9c', '#34495e', '#e67e22'
    ]
    return random.choice(colors)


@router.get("/role-distribution")
async def get_role_distribution() -> Dict[str, Any]:
    """
    👤 Jobs nach Rollen (Pie Chart)

    Beispiel: Business Analyst, Data Scientist, etc.
    """
    try:
        db = SessionLocal()

        # Jobs pro Rolle zählen
        query = text("""
                     SELECT job_role, COUNT(*) AS count
                     FROM jobs
                     WHERE job_role IS NOT NULL
                     GROUP BY job_role
                     ORDER BY count DESC;
                     """)

        result = db.execute(query).fetchall()
        db.close()

        labels = [row[0] for row in result]
        data = [row[1] for row in result]

        return {
            "labels": labels,
            "datasets": [{
                "data": data,
                "backgroundColor": [
                    '#3498db', '#e74c3c', '#2ecc71', '#f39c12',
                    '#9b59b6', '#1abc9c', '#34495e', '#e67e22'
                ]
            }]
        }

    except Exception as e:
        logger.error(f"Fehler bei Rollen-Verteilung: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/level-progression")
async def get_level_progression() -> Dict[str, Any]:
    """
    📊 7-Ebenen-Modell Verteilung

    Level 1: Discovery (neue Skills)
    Level 2: ESCO Standard
    Level 3: Digital Skills
    Level 4: Fachbuch
    Level 5: Academia
    """
    try:
        db = SessionLocal()

        # Skills pro Level zählen
        query = text("""
                     SELECT level, COUNT(*) AS count
                     FROM skills
                     GROUP BY level
                     ORDER BY level;
                     """)

        result = db.execute(query).fetchall()
        db.close()

        level_names = {
            1: "Level 1: Discovery",
            2: "Level 2: ESCO",
            3: "Level 3: Digital",
            4: "Level 4: Fachbuch",
            5: "Level 5: Academia"
        }

        labels = [level_names.get(row[0], f"Level {row[0]}") for row in result]
        data = [row[1] for row in result]

        return {
            "labels": labels,
            "datasets": [{
                "label": "Skills pro Ebene",
                "data": data,
                "backgroundColor": '#2ecc71'
            }]
        }

    except Exception as e:
        logger.error(f"Fehler bei Level-Progression: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/emerging-skills")
async def get_emerging_skills() -> list[Dict[str, Any]]:
    """
    🚀 Top 10 aufstrebende Skills

    Vergleicht Häufigkeit: 2024 vs. 2023
    """
    try:
        db = SessionLocal()

        query = text("""
                     SELECT
                         s.label,
                         COUNT(CASE WHEN EXTRACT(YEAR FROM j.posting_date) = 2024 THEN 1 END) AS count_2024,
                         COUNT(CASE WHEN EXTRACT(YEAR FROM j.posting_date) = 2023 THEN 1 END) AS count_2023,
                         (COUNT(CASE WHEN EXTRACT(YEAR FROM j.posting_date) = 2024 THEN 1 END) -
                          COUNT(CASE WHEN EXTRACT(YEAR FROM j.posting_date) = 2023 THEN 1 END)) AS growth
                     FROM skills s
                              JOIN jobs j ON s.job_id = j.id
                     WHERE EXTRACT(YEAR FROM j.posting_date) IN (2023, 2024)
                     GROUP BY s.label
                     HAVING growth > 0
                     ORDER BY growth DESC
                         LIMIT 10;
                     """)

        result = db.execute(query).fetchall()
        db.close()

        return [
            {
                "skill": row[0],
                "growth": row[3],
                "growth_pct": round((row[1] / max(row[2], 1) - 1) * 100, 1)
            }
            for row in result
        ]

    except Exception as e:
        logger.error(f"Fehler bei Emerging Skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))
