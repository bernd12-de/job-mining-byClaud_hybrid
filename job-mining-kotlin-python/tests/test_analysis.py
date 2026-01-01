# tests/test_analysis.py
from unittest.mock import MagicMock
from app.infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor

def test_assistenz_digital_shift():
    mock_repo = MagicMock()
    # Labels müssen im Text vorkommen
    mock_repo.get_all_identifiable_labels.return_value = ["Cloud-Software", "Koordination"]
    mock_repo.get_all_identifiable_labels.return_value = ["Cloud-Software", "Koordination"]
    mock_repo.get_level.side_effect = lambda term: 4 if "Cloud" in term else 2
    mock_repo.is_digital_skill.side_effect = lambda term: "Cloud" in term

    mock_manager = MagicMock()
    # Sicherstellen, dass das DTO ein Attribut 'original_term' hat
    mock_manager.create_competence_dto.side_effect = lambda **k: MagicMock(original_term=k['original_term'], is_digital=k['is_digital'], level=k['level'], role_context=k['role_context'])

    extractor = SpaCyCompetenceExtractor(repository=mock_repo, manager=mock_manager)
    text = "Die Assistenz nutzt Cloud-Software zur Koordination."

    results = extractor.extract_competences(text, "Assistenz")

    # Behebt IndexError: list index out of range
    cloud_skills = [r for r in results if "Cloud" in r.original_term]
    assert len(cloud_skills) > 0
    assert cloud_skills[0].is_digital == True
