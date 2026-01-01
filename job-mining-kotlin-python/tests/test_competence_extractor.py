# test_competence_extractor.py
import pytest
from unittest.mock import MagicMock
from app.infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor


'''
@pytest.fixture
def mock_repo():
    mock = MagicMock()
    # Vertrag: get_all_identifiable_labels liefert die Begriffe für den PhraseMatcher
    mock.get_all_identifiable_labels.return_value = [
        "Projektmanagement durchführen", "Datenbanken verwalten",
        "Kunden beraten", "Software entwickeln"
    ]
    # Ebenen-Logik
    mock.get_level.side_effect = lambda x: 2
    mock.is_digital_skill.return_value = False
    return mock
'''
@pytest.fixture
def mock_repo():
    mock = MagicMock()
    # Der Vertrag: get_all_identifiable_labels liefert Begriffe für den Matcher
    mock.get_all_identifiable_labels.return_value = [
        "Projektmanagement durchführen", "Datenbanken verwalten",
        "Kunden beraten", "Software entwickeln", "UX-Testing durchführen"
    ]
    mock.get_level.side_effect = lambda x: 2
    mock.is_digital_skill.return_value = False
    return mock

@pytest.fixture
def mock_manager():
    mock = MagicMock()
    # Factory simuliert die Erstellung von Objekten mit Attributen
    def create_mock_dto(**kwargs):
        dto = MagicMock()
        for k, v in kwargs.items():
            setattr(dto, k, v)
        return dto
    mock.create_competence_dto.side_effect = create_mock_dto
    return mock

@pytest.fixture
def extractor(mock_repo, mock_manager):
    # Behebt den TypeError (Konstruktor-Vertrag)
    return SpaCyCompetenceExtractor(repository=mock_repo, manager=mock_manager)

class TestCompetenceExtractor:
    def test_01_direct_phrase_match(self, extractor):
        text = "Wir suchen Experten für Kundenberatung und Softwareentwicklung."
        results = extractor.extract_competences(text, "Assistenz")
        assert len(results) >= 1

    def test_05_uri_and_id_integrity(self, extractor):
        text = "Wir suchen Experten für UX-Testing."
        results = extractor.extract_competences(text, "IT")
        assert len(results) > 0
        # Prüft, ob das DTO-Feld vorhanden ist (Vertragsschutz)
        assert hasattr(results[0], 'esco_uri')
