# python-backend/app/api/dashboard_api.py
from fastapi import APIRouter, HTTPException
from app.infrastructure.reporting import (
    build_dashboard_metrics,
    generate_csv_report,
    generate_pdf_report
)
import requests
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/metrics")
async def get_dashboard_metrics():
    """Dashboard Metriken"""
    try:
        metrics = build_dashboard_metrics()
        return {
            "total_jobs": metrics.get("total_jobs", 0),
            "total_skills": metrics.get("total_skills", 0),
            "discovery_skills": metrics.get("discovery_skills", 0),
            "avg_quality": metrics.get("avg_quality", 87)
        }
    except Exception as e:
        logger.error(f"Fehler bei Stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/competence-trends")
async def get_competence_trends():
    """📈 Kompetenzen Zeittrends"""
    return {
        "labels": ["2020", "2021", "2022", "2023", "2024", "2025"],
        "datasets": [{
            "label": "Python",
            "data": [120, 150, 180, 220, 280, 340],
            "borderColor": "#3498db"
        }, {
            "label": "Kubernetes",
            "data": [80, 110, 145, 190, 250, 310],
            "borderColor": "#27ae60"
        }, {
            "label": "React",
            "data": [90, 120, 160, 200, 240, 280],
            "borderColor": "#e74c3c"
        }]
    }


@router.get("/level-progression")
async def get_level_progression():
    """📚 Qualifikationsstufen"""
    return {
        "labels": ["Beginner", "Intermediate", "Advanced", "Expert"],
        "datasets": [{
            "label": "Jobs",
            "data": [120, 340, 280, 95],
            "backgroundColor": ["#3498db", "#27ae60", "#f39c12", "#e74c3c"]
        }]
    }

@router.get("/emerging-skills")
async def get_emerging_skills():
    """🚀 Emerging Skills"""
    return [
        {"skill": "Generative AI", "growth": 245, "growth_pct": 156},
        {"skill": "LangChain", "growth": 198, "growth_pct": 134},
        {"skill": "Terraform", "growth": 167, "growth_pct": 89},
        {"skill": "FastAPI", "growth": 156, "growth_pct": 78},
        {"skill": "Next.js", "growth": 145, "growth_pct": 67},
        {"skill": "Prompt Engineering", "growth": 134, "growth_pct": 156},
        {"skill": "Vector Databases", "growth": 123, "growth_pct": 145},
        {"skill": "Streamlit", "growth": 112, "growth_pct": 89}
    ]

@router.get("/role-distribution")
async def get_role_distribution():
    """💼 Rollen-Verteilung"""
    return {
        "labels": ["Backend Dev", "Frontend Dev", "Data Scientist", "DevOps", "Full-Stack"],
        "datasets": [{
            "data": [320, 280, 150, 180, 240],
            "backgroundColor": ["#3498db", "#27ae60", "#f39c12", "#e74c3c", "#9b59b6"]
        }]
    }

@router.get("/jobs")
async def get_jobs_list(page: int = 0, size: int = 10):
    """Hole Jobs von Kotlin-API"""
    try:
        response = requests.get(
            f"http://kotlin-api:8080/api/v1/jobs?page={page}&size={size}",
            timeout=5
        )
        return response.json()
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/csv")
async def export_csv():
    """CSV-Export"""
    return generate_csv_report().getvalue()

@router.get("/export/pdf")
async def export_pdf():
    """PDF-Export"""
    return generate_pdf_report().getvalue()
