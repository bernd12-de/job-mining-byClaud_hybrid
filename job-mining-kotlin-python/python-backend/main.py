import os
import sys
import logging
from logging import Logger

from warnings import catch_warnings

import streamlit as st
import pandas as pd
import requests

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, requests
from typing import List, Dict
import subprocess

# --- 1. KORREKTE IMPORTE (Mit 'app.' Prefix) ---
from app.domain.models import AnalysisResultDTO
from app.interfaces.interfaces import IJobMiningWorkflowManager

# Infrastruktur
from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
from app.infrastructure.repositories.hybrid_competence_repository import HybridCompetenceRepository
from app.infrastructure.extractor.advanced_text_extractor import AdvancedTextExtractor
from app.infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor
from app.infrastructure.extractor.fuzzy_competence_extractor import FuzzyCompetenceExtractor
from app.infrastructure.extractor.competence_extractor import CompetenceExtractor
from app.infrastructure.extractor.discovery_extractor import DiscoveryExtractor
from app.infrastructure.extractor.metadata_extractor import MetadataExtractor
from app.infrastructure.exporter import save_result, rebuild_summary
from app.infrastructure.io.job_directory_processor import JobDirectoryProcessor

# Domain Services
from app.application.services.organization_service import OrganizationService
from app.application.services.role_service import RoleService

# Orchestrator
from app.application.job_mining_workflow_manager import JobMiningWorkflowManager

# API Helper
from app.core.api_endpoints import scrape_and_analyze_url, URLInput
from app.api.dashboard_api import router as dashboard_router
from dashboard_app import PYTHON_API_BASE

1
# --- 2. SETUP & LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PyMain")

BASE_DATA_DIR = os.getenv("BASE_DATA_DIR", "data")
JOB_DIR = os.path.join(BASE_DATA_DIR, "jobs")

app = FastAPI(title="Job Mining Python Analysis Engine", version="2.3.0")

# ✅ Dashboard-Routes hinzufügen
app.include_router(dashboard_router)

# =========================================================
# 3. SYSTEM-VERDRAHTUNG (WIRING) MIT FEHLERBEHANDLUNG
# =========================================================
logger.info("🔧 Initialisiere Komponenten...")

try:
    # A. Basis (SSoT)
    RULE_CLIENT = KotlinRuleClient()


    # Repository (Keine Selbst-Importe mehr!)
    COMPETENCE_REPOSITORY = HybridCompetenceRepository(rule_client=RULE_CLIENT)

    # B. Extraktoren
    TEXT_EXTRACTOR = AdvancedTextExtractor()
    METADATA_EXTRACTOR = MetadataExtractor()

    # C. Services (FIX: RuleClient wird übergeben!)
    ORG_SERVICE = OrganizationService(rule_client=RULE_CLIENT)

    # RoleService (Fehlerabfangung, falls alte Version ohne Client)
    try:
        ROLE_SERVICE = RoleService(rule_client=RULE_CLIENT)
    except TypeError:
        logger.info("ℹ️ RoleService nutzt Standard-Init (kein RuleClient).")
        ROLE_SERVICE = RoleService()

    # D. NLP components (SpaCy + Fuzzy + Discovery)
    # Create base extractors first
    SPACY_EXT = SpaCyCompetenceExtractor(repository=COMPETENCE_REPOSITORY)
    FUZZY_EXT = FuzzyCompetenceExtractor(repository=COMPETENCE_REPOSITORY)

    # E. Manager: temporarily wire SPACY_EXT as placeholder, will be replaced after Discovery is constructed
    WORKFLOW_MANAGER = JobMiningWorkflowManager(
        text_extractor=TEXT_EXTRACTOR,
        competence_extractor=SPACY_EXT,  # placeholder
        organization_service=ORG_SERVICE,
        role_service=ROLE_SERVICE,
        metadata_extractor=METADATA_EXTRACTOR
    )

    # Discovery extractor needs a reference to the manager
    DISCOVERY_EXT = DiscoveryExtractor(repository=COMPETENCE_REPOSITORY, manager=WORKFLOW_MANAGER)

    # Now build the full CompetenceExtractor - pass shared spaCy model to avoid duplicate loading
    COMPETENCE_EXTRACTOR = CompetenceExtractor(
        spacy_ext=SPACY_EXT,
        fuzzy_ext=FUZZY_EXT,
        discovery_ext=DISCOVERY_EXT,
        nlp_model=SPACY_EXT.nlp  # Share the model to avoid loading twice
    )
    # Inject the real competence extractor into the manager
    WORKFLOW_MANAGER.competence_extractor = COMPETENCE_EXTRACTOR

    # F. Batch
    DIRECTORY_PROCESSOR = JobDirectoryProcessor(
        manager=WORKFLOW_MANAGER,
        base_path=JOB_DIR
    )

    logger.info("✅ System erfolgreich verdrahtet.")

except ImportError as e:
    logger.error(f"❌ Fehler beim Importieren von Modulen: {e}")
    logger.error("   Bitte führen Sie 'pip install -r requirements.txt' aus.")
    sys.exit(1)
except Exception as e:
    logger.error(f"❌ Kritischer Fehler bei der System-Initialisierung: {e}", exc_info=True)
    logger.error("   System kann nicht gestartet werden!")
    sys.exit(1)


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




# =========================================================
# 4. API ENDPUNKTE (ANGEPASST AN KOTLIN-ERWARTUNG)
# =========================================================


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

try:
    KOTLIN_API_BASE, PYTHON_API_BASE = _detect_api_endpoints()
    logger.info(f"🌐 API Endpoints - Kotlin: {KOTLIN_API_BASE}, Python: {PYTHON_API_BASE}")

except Exception as e:
    Logger.warning("❌ Fehler beim Erkennen der API Endpoints, verwende Defaults.")







@app.on_event("startup")
async def startup_event():
    """Startup mit umfassender Fehlerbehandlung"""
    try:
        logger.info("🚀 API startet...")
        if not os.path.exists(JOB_DIR):
            os.makedirs(JOB_DIR, exist_ok=True)

        # Check Repo mit Fehlerbehandlung
        try:
            if len(COMPETENCE_REPOSITORY.get_all_skills()) == 0:
                logger.warning("⚠️ Repository leer. Trigger Nachladen...")
                if hasattr(COMPETENCE_REPOSITORY, "_load_data"):
                    COMPETENCE_REPOSITORY._load_data()
        except Exception as e:
            logger.error(f"⚠️ Fehler beim Laden des Repositories: {e}")
            logger.info("   System läuft weiter mit Fallback-Daten...")
    except Exception as e:
        logger.error(f"❌ Kritischer Fehler beim Startup: {e}")
        logger.info("   System versucht trotzdem zu starten...")

@st.cache_data(ttl=60)
def fetch_discovery_candidates():
    try:
        response = requests.get(f"{PYTHON_API_BASE}/discovery/candidates", timeout=5)
        if response.status_code == 200:
            data = response.json()
            # 🔧 FIX: Prüfe ob data eine Liste ist
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return data.get('candidates', [])
            return []
        return []
    except Exception as e:
        logger.error(f"Fehler: {e}")
        return []




# MAIN SEITE
st.set_page_config(page_title="Dashboard | Job Mining", page_icon="📊", layout="wide")

st.title("📊 Job Mining Dashboard")

candidates = fetch_discovery_candidates()

if candidates:
    for candidate in candidates[:10]:
        col1, col2, col3 = st.columns([3, 1, 2])

        with col1:
            st.markdown(f"**{candidate.get('text', 'N/A')}**")

        with col2:
            st.metric("Häufigkeit", candidate.get('occurrences', 0))

        with col3:
            if st.button("✅ Approve", key=f"approve_{candidate.get('id')}"):
                if approve_candidate(candidate.get('id')):
                    st.success("Approved!")

            if st.button("🚫 Ignore", key=f"ignore_{candidate.get('id')}"):
                if ignore_candidate(candidate.get('id')):
                    st.success("Ignored!")
else:
    st.info("Keine Daten verfügbar.")



# --- PFAD-FIX 1: /analyse/file statt /analyse ---
@app.post("/analyse/file", response_model=AnalysisResultDTO)
async def analyze_file(file: UploadFile = File(...)):
    """Upload-Endpunkt für Kotlin (PDF/DOCX) mit robuster Fehlerbehandlung."""
    logger.info(f"📥 [POST /analyse/file] Datei: {file.filename}")
    try:
        # Validierung
        if not file.filename:
            raise HTTPException(status_code=400, detail="Dateiname fehlt")

        # Dateiinhalt prüfen
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Datei ist leer")

        # Reset file pointer für weitere Verarbeitung
        from io import BytesIO
        file_obj = BytesIO(content)

        return await WORKFLOW_MANAGER.run_full_analysis(file_obj, file.filename)
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"❌ Validierungsfehler: {e}")
        raise HTTPException(status_code=400, detail=f"Validierungsfehler: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Interner Fehler bei Dateianalyse: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analyse fehlgeschlagen: {str(e)}")




# --- PFAD-FIX 2: /analyse/scrape-url statt /scrape-url ---
@app.post("/analyse/scrape-url", response_model=AnalysisResultDTO)
async def scrape_url_endpoint(url_input: URLInput):
    """Scraping-Endpunkt mit Fehlerbehandlung."""
    logger.info(f"🌍 [POST /analyse/scrape-url] URL: {url_input.url}")
    try:
        if not url_input.url or not url_input.url.strip():
            raise HTTPException(status_code=400, detail="URL fehlt oder ist leer")
        result = await scrape_and_analyze_url(url_input, manager=WORKFLOW_MANAGER)
        try:
            save_result(result)
            rebuild_summary()
        except Exception as e:
            logger.warning(f"Export fehlgeschlagen: {e}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler beim URL-Scraping: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scraping fehlgeschlagen: {str(e)}")


# --- PFAD-FIX 3: /system/status statt /health ---
@app.get("/system/status")
def system_status():
    """Health-Check für Kotlin mit robuster Fehlerbehandlung."""
    try:
        skills_count = 0
        try:
            skills_count = len(COMPETENCE_REPOSITORY.get_all_skills())
        except Exception as e:
            logger.warning(f"Fehler beim Abrufen der Skills: {e}")

        return {
            "status": "UP",
            "service": "python-backend",
            "skills_loaded": skills_count,
            "version": "2.3.0"
        }
    except Exception as e:
        logger.error(f"❌ Fehler im Status-Check: {e}")
        return {
            "status": "DEGRADED",
            "service": "python-backend",
            "error": str(e)
        }

# --- PFAD-FIX 4: /role-mappings (NEU) ---
@app.get("/role-mappings")
def get_role_mappings():
    """
    Gibt die aktiven Rollen-Mappings zurück, damit Kotlin den Status prüfen kann.
    """
    # Versuche Mappings aus dem RoleService oder RuleClient zu holen
    mappings = {}
    if hasattr(ROLE_SERVICE, 'role_mappings'):
        mappings = ROLE_SERVICE.role_mappings
    elif hasattr(RULE_CLIENT, '_get_static_fallback_role_mappings'):
        mappings = RULE_CLIENT._get_static_fallback_role_mappings()

    return {
        "count": len(mappings),
        "mappings": mappings
    }

# --- DASHBOARD / REPORTING ENDPOINTS ---
from fastapi.responses import StreamingResponse
from app.infrastructure.reporting import build_dashboard_metrics, generate_csv_report, generate_pdf_report

@app.get("/reports/dashboard-metrics")
def get_dashboard_metrics(top_n: int = 10):
    """Aggregierte Metriken für das Dashboard (Top Skills, Domain Mix, Zeitreihen)"""
    metrics = build_dashboard_metrics(top_n=top_n)
    return metrics


@app.get("/reports/export.csv")
def download_csv_report():
    """Generiert einen CSV-Export der aktuell verarbeiteten Jobs."""
    csv_bio = generate_csv_report()
    return StreamingResponse(csv_bio, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=job_mining_data_report.csv"})


@app.get("/reports/export.pdf")
def download_pdf_report():
    """Generiert einen einfachen PDF-Report der aktuell verarbeiteten Jobs."""
    pdf_bio = generate_pdf_report()
    return StreamingResponse(pdf_bio, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=job_mining_report.pdf"})


# Bestehende Pfade (waren bereits korrekt/grün)
@app.post("/batch-process", response_model=List[AnalysisResultDTO])
async def trigger_batch():
    """Batch-Verarbeitung mit Fehlerbehandlung"""
    logger.info("📦 [POST /batch-process] Starte...")
    try:
        results = await DIRECTORY_PROCESSOR.process_all_jobs()
        try:
            for r in results:
                save_result(r)
            rebuild_summary()
        except Exception as e:
            logger.warning(f"Batch-Export fehlgeschlagen: {e}")
        logger.info(f"📦 Batch fertig: {len(results)} Dateien analysiert.")
        return results
    except Exception as e:
        logger.error(f"❌ Fehler bei Batch-Verarbeitung: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch-Verarbeitung fehlgeschlagen: {str(e)}")

@app.post("/internal/admin/refresh-knowledge")
def refresh_knowledge():
    """Knowledge-Base-Refresh mit umfassender Fehlerbehandlung"""
    logger.info("🔄 [POST /refresh-knowledge] Refresh...")
    try:
        errors = []

        # Repository-Daten neu laden
        if hasattr(COMPETENCE_REPOSITORY, "_load_data"):
            try:
                COMPETENCE_REPOSITORY._load_data()
            except Exception as e:
                logger.error(f"Fehler beim Laden der Basis-Daten: {e}")
                errors.append(f"_load_data: {str(e)}")

        if hasattr(COMPETENCE_REPOSITORY, "_load_custom_skills"):
            try:
                COMPETENCE_REPOSITORY._load_custom_skills()
            except Exception as e:
                logger.error(f"Fehler beim Laden der Custom Skills: {e}")
                errors.append(f"_load_custom_skills: {str(e)}")

        if hasattr(COMPETENCE_REPOSITORY, "_load_dynamic_blacklist"):
            try:
                COMPETENCE_REPOSITORY._load_dynamic_blacklist()
            except Exception as e:
                logger.error(f"Fehler beim Laden der Blacklist: {e}")
                errors.append(f"_load_dynamic_blacklist: {str(e)}")

        # WICHTIG: Extractor NICHT neu initialisieren! Das führt zu Memory-Problemen und Container-Crash.
        # Der Extractor wird die neuen Daten automatisch über das Repository verwenden.
        # try:
        #     global COMPETENCE_EXTRACTOR, WORKFLOW_MANAGER
        #     COMPETENCE_EXTRACTOR = SpaCyCompetenceExtractor(repository=COMPETENCE_REPOSITORY)
        #     WORKFLOW_MANAGER.competence_extractor = COMPETENCE_EXTRACTOR
        # except Exception as e:
        #     logger.error(f"Fehler beim Neuinitialisieren des Extractors: {e}")
        #     errors.append(f"extractor_init: {str(e)}")

        skills_count = 0
        try:
            skills_count = len(COMPETENCE_REPOSITORY.get_all_skills())
        except Exception as e:
            logger.error(f"Fehler beim Zählen der Skills: {e}")

        result = {
            "status": "refreshed" if not errors else "partial",
            "skills": skills_count
        }

        if errors:
            result["errors"] = errors
            result["message"] = "Refresh teilweise erfolgreich mit Fehlern"

        return result

    except Exception as e:
        logger.error(f"❌ Kritischer Fehler beim Refresh: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Refresh fehlgeschlagen: {str(e)}")


# =========================================================
# DISCOVERY API ENDPOINTS
# =========================================================
from pydantic import BaseModel


class DiscoveryApproval(BaseModel):
    terms: List[str]


class DiscoveryIgnore(BaseModel):
    terms: List[str]


@app.get("/discovery/candidates")
def get_discovery_candidates():
    """
    📋 Liefert alle entdeckten Kandidaten aus candidates.json
    """
    try:
        from app.infrastructure.extractor.discovery_logger import _data_base_dir, _ensure_discovery_dir
        base = _data_base_dir()
        ddir = _ensure_discovery_dir(base)
        fpath = ddir / "candidates.json"

        if not fpath.exists():
            return {"candidates": [], "total": 0}

        import json
        candidates = json.loads(fpath.read_text(encoding="utf-8")) or []
        # Sortiere nach count (häufigste zuerst)
        candidates.sort(key=lambda x: x.get("count", 0), reverse=True)

        return {
            "candidates": candidates,
            "total": len(candidates)
        }
    except Exception as e:
        logger.error(f"❌ Error loading candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/discovery/approved")
def get_approved_skills():
    """
    ✅ Liefert alle genehmigten Skills aus approved_skills.json
    """
    try:
        from app.infrastructure.extractor.discovery_logger import _data_base_dir, _ensure_discovery_dir
        base = _data_base_dir()
        ddir = _ensure_discovery_dir(base)
        fpath = ddir / "approved_skills.json"

        if not fpath.exists():
            return {"approved": {}, "total": 0}

        import json
        approved = json.loads(fpath.read_text(encoding="utf-8")) or {}

        return {
            "approved": approved,
            "total": len(approved)
        }
    except Exception as e:
        logger.error(f"❌ Error loading approved skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/discovery/ignored")
def get_ignored_skills():
    """
    🚫 Liefert alle ignorierten Terms aus ignore_skills.json
    """
    try:
        from app.infrastructure.extractor.discovery_logger import _data_base_dir, _ensure_discovery_dir
        base = _data_base_dir()
        ddir = _ensure_discovery_dir(base)
        fpath = ddir / "ignore_skills.json"

        if not fpath.exists():
            return {"ignored": [], "total": 0}

        import json
        ignored = json.loads(fpath.read_text(encoding="utf-8")) or []

        return {
            "ignored": ignored,
            "total": len(ignored)
        }
    except Exception as e:
        logger.error(f"❌ Error loading ignored skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/discovery/approve")
def approve_candidates(approval: DiscoveryApproval):
    """
    ✅ Genehmigt Kandidaten → Verschiebt von candidates.json zu approved_skills.json
    """
    try:
        from app.infrastructure.extractor.discovery_logger import _data_base_dir, _ensure_discovery_dir
        import json

        base = _data_base_dir()
        ddir = _ensure_discovery_dir(base)
        candidates_path = ddir / "candidates.json"
        approved_path = ddir / "approved_skills.json"

        # Lade bestehende Daten
        candidates = json.loads(candidates_path.read_text(encoding="utf-8")) if candidates_path.exists() else []
        approved = json.loads(approved_path.read_text(encoding="utf-8")) if approved_path.exists() else {}

        # Normalisiere terms zu lowercase
        terms_lower = {t.lower().strip() for t in approval.terms}

        # Finde und verschiebe
        to_approve = [c for c in candidates if c.get("term", "").lower().strip() in terms_lower]
        candidates = [c for c in candidates if c.get("term", "").lower().strip() not in terms_lower]

        # Füge zu approved hinzu (als Mapping: term -> term, für Custom Skills kompatibel)
        for item in to_approve:
            term = item.get("term")
            if term:
                approved[term] = term  # Simple 1:1 mapping

        # Speichere
        candidates_path.write_text(json.dumps(candidates, ensure_ascii=False, indent=2), encoding="utf-8")
        approved_path.write_text(json.dumps(approved, ensure_ascii=False, indent=2), encoding="utf-8")

        logger.info(f"✅ Approved {len(to_approve)} candidates")
        return {
            "status": "success",
            "approved_count": len(to_approve),
            "remaining_candidates": len(candidates)
        }
    except Exception as e:
        logger.error(f"❌ Error approving candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/discovery/ignore")
def ignore_candidates(ignore: DiscoveryIgnore):
    """
    🚫 Ignoriert Kandidaten → Verschiebt von candidates.json zu ignore_skills.json
    """
    try:
        from app.infrastructure.extractor.discovery_logger import _data_base_dir, _ensure_discovery_dir
        import json

        base = _data_base_dir()
        ddir = _ensure_discovery_dir(base)
        candidates_path = ddir / "candidates.json"
        ignore_path = ddir / "ignore_skills.json"

        # Lade bestehende Daten
        candidates = json.loads(candidates_path.read_text(encoding="utf-8")) if candidates_path.exists() else []
        ignored = json.loads(ignore_path.read_text(encoding="utf-8")) if ignore_path.exists() else []

        # Normalisiere terms
        terms_lower = {t.lower().strip() for t in ignore.terms}

        # Entferne aus candidates
        to_ignore = [c.get("term") for c in candidates if c.get("term", "").lower().strip() in terms_lower]
        candidates = [c for c in candidates if c.get("term", "").lower().strip() not in terms_lower]

        # Füge zu ignored hinzu
        ignored.extend(to_ignore)
        ignored = list(set(ignored))  # Duplikate entfernen

        # Speichere
        candidates_path.write_text(json.dumps(candidates, ensure_ascii=False, indent=2), encoding="utf-8")
        ignore_path.write_text(json.dumps(ignored, ensure_ascii=False, indent=2), encoding="utf-8")

        logger.info(f"🚫 Ignored {len(to_ignore)} candidates")
        return {
            "status": "success",
            "ignored_count": len(to_ignore),
            "remaining_candidates": len(candidates)
        }
    except Exception as e:
        logger.error(f"❌ Error ignoring candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/discovery/candidates")
def clear_candidates():
    """
    🗑️ Löscht alle Kandidaten (candidates.json leeren)
    """
    try:
        from app.infrastructure.extractor.discovery_logger import _data_base_dir, _ensure_discovery_dir

        base = _data_base_dir()
        ddir = _ensure_discovery_dir(base)
        fpath = ddir / "candidates.json"

        fpath.write_text("[]", encoding="utf-8")

        logger.info("🗑️ Cleared all candidates")
        return {"status": "success", "message": "All candidates cleared"}
    except Exception as e:
        logger.error(f"❌ Error clearing candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))





def main():
    st.title("🔍 Discovery: Neue Skills Management")
    st.caption("Selbstlernendes System für automatische Skill-Erkennung")

    # Stats
    candidates = fetch_discovery_candidates()

    # Sichere Filterung mit Typ-Überprüfung
    skills = [c for c in candidates if isinstance(c, dict) and c.get('entity_type') == 'skill']
    pending = [c for c in candidates if isinstance(c, dict) and c.get('status') == 'pending']

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🆕 Neue Skills", len(skills))
    with col2:
        st.metric("⏳ Pending", len(pending))
    with col3:
        st.metric("✅ Auto-Promoted", len([c for c in candidates if isinstance(c, dict) and c.get('level', 0) >= 2]))
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
                filtered = [c for c in candidates if isinstance(c, dict) and c.get('entity_type') == 'skill']
            elif filter_type == "Rollen":
                filtered = [c for c in candidates if isinstance(c, dict) and c.get('entity_type') == 'role']
            elif filter_type == "Industrien":
                filtered = [c for c in candidates if isinstance(c, dict) and c.get('entity_type') == 'industry']

            # Tabelle
            for candidate in filtered[:20]:
                if not isinstance(candidate, dict):
                    continue

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
                {'Type': 'Skills', 'Anzahl': len([c for c in candidates if isinstance(c, dict) and c.get('entity_type') == 'skill'])},
                {'Type': 'Rollen', 'Anzahl': len([c for c in candidates if isinstance(c, dict) and c.get('entity_type') == 'role'])},
                {'Type': 'Industrien', 'Anzahl': len([c for c in candidates if isinstance(c, dict) and c.get('entity_type') == 'industry'])},
            ])

            st.bar_chart(df.set_index('Type'))

            # Level-Verteilung
            level_dist = {}
            for c in candidates:
                if isinstance(c, dict):
                    level = c.get('level', 1)
                    level_dist[level] = level_dist.get(level, 0) + 1

            st.markdown("### Level-Verteilung")
            st.bar_chart(level_dist)
        else:
            st.info("Keine Daten vorhanden.")

if __name__ == "__main__":
    main()



#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)

# =========================================================
# ADMIN: Playwright Installation
# =========================================================
@app.post("/internal/admin/install-playwright")
def install_playwright():
    """
    Versucht die Playwright-Installation (Python-Paket + Chromium mit Abhängigkeiten) durchzuführen.
    Nutzt apt-get über '--with-deps'. Läuft nur im Container sinnvoll.
    """
    try:
        # Installiere Python-Paket
        subprocess.run(["python3","-m","pip","install","playwright"], check=True)
        # Installiere Browser und System-Abhängigkeiten
        try:
            subprocess.run(["playwright","install","chromium","--with-deps"], check=True)
            return {"status":"installed", "mode": "with-deps"}
        except subprocess.CalledProcessError as e:
            # Fallback für Debian/Ubuntu Paketinkompatibilitäten: versuche Fonts + plain install
            try:
                subprocess.run(["apt-get","update"], check=True)
                # Debian/Ubuntu kompatible Fonts (Playwright benötigt Fonts für Rendering)
                subprocess.run(["apt-get","install","-y",
                                "fonts-unifont",
                                "fonts-ubuntu",
                                "fonts-dejavu-core"], check=True)
            except Exception:
                # Fonts-Installation ist optional – nicht als harter Fehler behandeln
                pass
            # Versuche ohne '--with-deps' (nur Browser herunterladen)
            subprocess.run(["playwright","install","chromium"], check=True)
            return {"status":"installed", "mode": "fallback-no-deps"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Installation fehlgeschlagen: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unerwarteter Fehler: {e}")

