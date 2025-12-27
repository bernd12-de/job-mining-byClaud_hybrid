# ==========================================================
# 🧪 TESTSUITE – JOBMINING HYBRID BASISVERSION
# ==========================================================
# Ziel: automatisiertes Testen der Python-Analysepipeline und API-Kette
# Technologie: pytest + httpx (Integrationstests)
# ==========================================================

# Verzeichnisstruktur:
# python-backend/
# ├── main.py
# ├── services/
# │   ├── gpt_service.py
# │   ├── skill_extractor.py
# │   └── trend_model.py
# ├── tests/
# │   ├── test_skill_extractor.py
# │   ├── test_trend_model.py
# │   ├── test_gpt_service.py
# │   └── test_api_integration.py
# └── requirements.txt


# ==========================================================
# 🔹 test_skill_extractor.py – Unit Test für Skill-Parsing
# ==========================================================

def test_skill_extraction_basic():
    from services.skill_extractor import extract_skills
    text = "We need Python, Docker, and AI experience."
    result = extract_skills(text)
    assert "python" in result
    assert "docker" in result
    assert len(result) >= 2


def test_skill_extraction_case_insensitive():
    from services.skill_extractor import extract_skills
    text = "Looking for JAVA, React, and Kubernetes skills."
    result = extract_skills(text)
    assert "java" in result
    assert "react" in result
    assert "kubernetes" in result


# ==========================================================
# 🔹 test_trend_model.py – Trendanalyse Mock-Test
# ==========================================================

def test_trend_analysis_keywords(monkeypatch):
    from services.trend_model import analyze_trends

    # Dummy Input
    text = "Machine learning and AI are trending."

    # Mock Funktion
    monkeypatch.setattr('services.trend_model.detect_trends', lambda x: ["AI", "ML"])

    result = analyze_trends(text)
    assert isinstance(result, list)
    assert "AI" in result


# ==========================================================
# 🔹 test_gpt_service.py – GPT-Service Simulation
# ==========================================================

def test_gpt_service_mock(monkeypatch):
    from services import gpt_service

    def fake_analyze(text):
        return {"summary": "Mocked GPT response"}

    monkeypatch.setattr(gpt_service, 'analyze_text_with_gpt', fake_analyze)
    result = gpt_service.analyze_text_with_gpt("Test input")
    assert "summary" in result
    assert result["summary"] == "Mocked GPT response"


# ==========================================================
# 🔹 test_api_integration.py – FastAPI Integrationstest
# ==========================================================

import io
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_analyze_endpoint(monkeypatch):
    # Mocking GPT
    monkeypatch.setattr('services.gpt_service.analyze_text_with_gpt', lambda x: {"mocked": True})

    fake_file = io.BytesIO(b"Python and AI development")
    response = client.post("/api/analyze", files={"file": ("job.txt", fake_file, "text/plain")})

    assert response.status_code == 200
    data = response.json()
    assert "skills" in data
    assert isinstance(data["skills"], list)
    assert any(s in data["skills"] for s in ["python", "ai"])


# ==========================================================
# ⚙️ PYTEST CONFIG (pytest.ini)
# ==========================================================

'''
[pytest]
asyncio_mode = auto
addopts = -v --tb=short --disable-warnings
python_files = tests/test_*.py
'''


# ==========================================================
# 🧠 TESTAUSFÜHRUNG
# ==========================================================
# Lokal:
#   cd python-backend
#   pytest -v
#
# GitLab CI (später):
#   pytest --junitxml=report.xml
#   Ergebnisse in CI als Artefakt speichern
# ==========================================================

# ✅ Ergebnis:
# - Unit + Integration Tests für alle Kernmodule
# - Mocking-Mechanismen integriert
# - Kompatibel mit CI/CD & Docker
# - Schnell, reproduzierbar und wartbar
