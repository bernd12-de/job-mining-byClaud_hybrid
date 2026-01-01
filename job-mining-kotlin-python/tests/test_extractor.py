# tests/test_extractor.py - KORRIGIERTE VERSION
from unittest.mock import MagicMock
from app.infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor

def test_level_assignment():
    # 1. Mock für das Repository (Der "Vertrag" für Daten)
    mock_repo = MagicMock()
    mock_repo.get_all_identifiable_labels.return_value = ["ERP-System"]
    # WICHTIG: Das Repo muss dem Extractor sagen, dass dies Ebene 4 ist
    mock_repo.get_level.return_value = 4

    mock_manager = MagicMock()
    # FIX: Die Factory muss ein Objekt mit echten Attributen erzeugen
    from app.domain.models import CompetenceDTO
    mock_manager.create_competence_dto.side_effect = lambda **kwargs: CompetenceDTO(
        original_term=kwargs.get('original_term', 'test'),
        esco_label="test", esco_uri="test", confidence_score=1.0,
        level=kwargs.get('level', 2), # Hier kommt die 4 rein!
        is_digital=False, role_context="test"
    )
    # 3. Initialisierung (Behebt den TypeError)
    extractor = SpaCyCompetenceExtractor(repository=mock_repo, manager=mock_manager)

    # 4. Extraktion (Behebt ValueError E195, da intern self.nlp(text) gerufen wird)
    results = extractor.extract_competences("Assistenz bedient ERP-System", "Assistenz")

    # Validierung des "Vertrags" (Ebene 4/5)
    assert results[0].level == 4
    assert results[0].original_term == "ERP-System"
