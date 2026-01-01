"""
NEUE HYBRID-ANWENDUNG V2.0
Main Entry Point - Clean Architecture
"""
import os
import sys
import argparse
from pathlib import Path

# Setup Pfade
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app.core.models_v2 import JobPosting, Competence
from app.infrastructure.repositories.hybrid_competence_repository import HybridCompetenceRepository
from app.infrastructure.extractor.spacy_competence_extractor import SpacyCompetenceExtractor
from app.infrastructure.data.esco_data_repository import EscoDataRepository

def main():
    """
    Orchestriert die Job-Mining-Pipeline V2.0
    """
    print("=" * 80)
    print("🚀 JOB MINING HYBRID APPLICATION V2.0")
    print("=" * 80)
    
    # 1. Repositories initialisieren
    print("\n📦 Initialisiere Repositories...")
    esco_repo = EscoDataRepository()
    competence_repo = HybridCompetenceRepository()
    
    # 2. Extractor initialisieren
    print("🧠 Starte spaCy NLP Extractor...")
    extractor = SpacyCompetenceExtractor(competence_repo)
    
    # 3. Zeige verfügbare Datenquellen
    print("\n📊 VERFÜGBARE DATENQUELLEN:")
    print(f"   - ESCO Skills geladen: {len(esco_repo.get_all_skills())}")
    print(f"   - Custom Skills geladen: {competence_repo._custom_labels.__len__()}")
    print(f"   - Digitale Skills: {len(competence_repo._fachbuch_skills)}")
    
    # 4. Test mit einer Sample-Jobanzeige
    sample_job_text = """
    Senior Python Developer (m/w/d)
    
    Wir suchen einen erfahrenen Python-Entwickler für unser Team.
    
    DEINE AUFGABEN:
    - Entwicklung von Web-Applikationen mit Django und FastAPI
    - Implementierung von REST APIs
    - Docker und Kubernetes Orchestrierung
    - CI/CD Pipeline Management mit Jenkins
    
    DEIN PROFIL:
    - 5+ Jahre Erfahrung mit Python
    - Kenntnisse in Git und agilen Methoden
    - Scrum Master Zertifizierung von Vorteil
    - Machine Learning Grundlagen
    - Cloud Erfahrung (AWS oder Azure)
    """
    
    print("\n🔍 Extrahiere Kompetenzen aus Testdokument...")
    competences = extractor.extract_competences(sample_job_text, role="IT & Softwareentwicklung")
    
    print(f"\n✅ {len(competences)} Kompetenzen erkannt:")
    for comp in competences[:10]:
        print(f"   - {comp.name} (Vertrauen: {comp.confidence:.2%})")
    
    # 5. Erstelle JobPosting-Objekt
    print("\n💾 Erstelle JobPosting-Entität...")
    job = JobPosting(
        job_id="sample_001",
        source_path="memory://sample",
        raw_text=sample_job_text,
        title="Senior Python Developer",
        company="Tech Company",
        location="Berlin",
        year=2025
    )
    job.competences = competences
    
    print(f"\n✨ JobPosting erstellt:")
    print(f"   Titel: {job.title}")
    print(f"   Ort: {job.location}")
    print(f"   Jahr: {job.year}")
    print(f"   Kompetenzen: {len(job.competences)}")
    
    print("\n" + "=" * 80)
    print("✅ V2.0 PIPELINE ERFOLGREICH!")
    print("=" * 80)

if __name__ == "__main__":
    main()
