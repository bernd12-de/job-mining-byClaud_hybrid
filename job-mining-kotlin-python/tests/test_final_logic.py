import pytest
from unittest.mock import MagicMock
from app.infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor
from app.domain.models import CompetenceDTO

# Mock für das Repository (simuliert geladene JSONs)
class MockRepo:
    def get_all_skills(self): return ["Excel", "Terminplanung"] # ESCO Ebene 2
    def is_digital_skill(self, term): return term.lower() == "cloud-computing" # Ebene 3
    def get_level(self, term):
        # Simuliert: "Cloud-Computing" steht im Fachbuch (Level 4)
        if term.lower() == "cloud-computing": return 4
        return 2

def test_assistenz_digital_shift():
    """
    Szenario: Eine Assistenz nutzt Cloud-Computing.
    Erwartung:
    - Excel -> Level 2 (Standard)
    - Cloud-Computing -> Level 4 (Fachbuch) + is_digital=True
    """
    repo = MockRepo()
    # Der MockRepo braucht zusätzlich diese Methode für den neuen Vertrag
    repo.get_all_identifiable_labels = lambda: ["Excel", "Cloud-Computing"]
    # Manager hinzufügen!
    mock_manager = MagicMock()
    mock_manager.create_competence_dto.side_effect = lambda **k: MagicMock(**k)

    # FIX: Manager übergeben
    extractor = SpaCyCompetenceExtractor(repository=repo, manager=mock_manager)

    #extractor = SpaCyCompetenceExtractor(repository=repo)

    text = "Wir suchen eine Assistenz für Excel und Cloud-Computing Aufgaben."
    role = "Assistenz"

    results = extractor.extract_competences(text, role)

    # 1. Prüfe Excel
    excel = next(r for r in results if r.original_term == "Excel")
    assert excel.level == 2, "Excel sollte Ebene 2 (Standard) sein"

    # 2. Prüfe Cloud-Computing
    cloud = next(r for r in results if r.original_term == "Cloud-Computing")
    assert cloud.level == 4, "Cloud-Computing sollte Ebene 4 (Fachbuch) sein"
    assert cloud.is_digital == True, "Cloud-Computing sollte digital sein"
    assert cloud.role_context == "Assistenz", "Kontext muss erhalten bleiben"

    print("\n✅ TEST ERFOLGREICH: Digital Shift wurde erkannt!")
