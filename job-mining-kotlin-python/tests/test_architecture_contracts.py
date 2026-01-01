import pytest
from app.infrastructure.repositories.hybrid_competence_repository import HybridCompetenceRepository
from unittest.mock import MagicMock

def test_repository_interface_contract():
    """
    SICHERHEITS-CHECK: Dieser Test stellt sicher, dass die KI keine
    lebenswichtigen Methoden umbenannt hat.
    """
    repo = HybridCompetenceRepository(rule_client=MagicMock())

    # Der 'Vertrag': Diese Methode MUSS existieren, egal was intern passiert
    assert hasattr(repo, 'get_all_identifiable_labels'), "🚨 VERTRAGSBRUCH: get_all_identifiable_labels fehlt!"

    # Teste Rückgabetyp (muss Liste sein)
    labels = repo.get_all_identifiable_labels()
    assert isinstance(labels, list), "🚨 VERTRAGSBRUCH: Methode muss eine Liste zurückgeben!"

def test_extractor_compatibility():
    """Prüft, ob der Extractor den Vertrag nutzt."""
    mock_repo = MagicMock()
    mock_repo.get_all_identifiable_labels.return_value = ["TestSkill"]

    from app.infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor
    # Wenn die KI hier den Konstruktor falsch umbaut, knallt es hier sofort
    extractor = SpaCyCompetenceExtractor(repository=mock_repo, manager=MagicMock())
    assert "KNOWLEDGE_BASE" in extractor.matcher, "Matcher wurde nicht korrekt initialisiert!"
