import sys
import os

# Sicherstellen, dass das Root-Verzeichnis im Path ist
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infrastructure.repositories.hybrid_competence_repository import HybridCompetenceRepository
from app.infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor
from app.infrastructure.extractor.metadata_extractor import MetadataExtractor
from app.application.job_mining_workflow_manager import JobMiningWorkflowManager

def run_poc():
    print("🧪 Starte Proof of Concept: Assistenz-Analyse (Ebenen 4 & 5)\n")

    class MockClient:
        base_url = "http://localhost:8080"
        def fetch_blacklist(self): return set()

    # Initialisierung
    repo = HybridCompetenceRepository(rule_client=MockClient())

    # Force-Injektion für den Test (überschreibt geladene JSONs für klare Ergebnisse)
    repo._esco_labels = {"Terminkalender", "Korrespondenz"}
    repo._fachbuch_set = {"cloud-architektur", "agile-methoden"}
    repo._academia_set = {"python-programmierung"}
    repo._digital_set = {"cloud-architektur"}

    comp_ext = SpaCyCompetenceExtractor(repository=repo)
    meta_ext = MetadataExtractor()

    mock_service = type('Mock', (object,), {
        'classify_industry': lambda x: "Dienstleistung",
        'classify_role': lambda job_text, job_title: "Assistenz & Office"
    })()

    manager = JobMiningWorkflowManager(
        text_extractor=None,
        competence_extractor=comp_ext,
        organization_service=mock_service,
        role_service=mock_service
    )

    job_text = """
    Wir suchen eine moderne Assistenz (m/w/d).
    Aufgaben: Klassische Terminkalender führen.
    Unterstützung bei Cloud-Architektur und Agile-Methoden.
    Erste Erfahrungen in Python-Programmierung erwünscht.
    """

    print("🔍 Analysiere Test-Anzeige...")
    result = manager._run_analysis_from_text(job_text, "test_assistenz.txt")

    print(f"\n📊 Ergebnis für Rolle: {result.job_role}")
    print("-" * 60)
    for comp in result.competences:
        lvl = repo.get_level_for_term(comp.original_term)
        print(f"Skill: {comp.original_term:25} | Ebene: {lvl}")

if __name__ == "__main__":
    run_poc()
