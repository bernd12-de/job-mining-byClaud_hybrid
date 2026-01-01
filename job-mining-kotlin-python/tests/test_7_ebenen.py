from unittest.mock import MagicMock
from app.infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor
from app.domain.models import CompetenceDTO

def test_assistenz_level_logic():
    # 1. Setup Mock Repository
    mock_repo = MagicMock()
    # WICHTIG: Die Labels müssen so im Mock stehen, wie sie im Text vorkommen (oder wie spaCy sie tokenisiert)
    # Der Matcher selbst nutzt 'LOWER', aber die Liste dient als Basis für die Patterns
    mock_repo.get_all_identifiable_labels.return_value = ["Excel", "Cloud"]

    # Side effects für die Ebenen-Logik (Ebene 2 für Standard, Ebene 4 für Innovation)
    mock_repo.get_level.side_effect = lambda term: 4 if "cloud" in term.lower() else 2
    mock_repo.is_digital_skill.side_effect = lambda term: "cloud" in term.lower()

    # 2. Setup Mock Manager (Factory für DTOs)
    mock_manager = MagicMock()
    # Wir simulieren die Erstellung eines echten DTOs, damit die Assertions auf Attribute zugreifen können
    def mock_create_dto(**kwargs):
        return CompetenceDTO(
            original_term=kwargs.get('original_term'),
            esco_label=kwargs.get('esco_label', 'label'),
            esco_uri=kwargs.get('esco_uri', 'uri'),
            confidence_score=1.0,
            level=kwargs.get('level', 2),
            is_digital=kwargs.get('is_digital', False),
            role_context=kwargs.get('role_context', 'Assistenz')
        )
    mock_manager.create_competence_dto.side_effect = mock_create_dto

    # 3. Initialisierung des Extractors mit dem neuen Vertrag
    extractor = SpaCyCompetenceExtractor(repository=mock_repo, manager=mock_manager)

    # 4. Test-Lauf: Unterschiedliche Schreibweisen simulieren
    # "Excel" (Groß) vs "cloud" (Klein) im Text
    text = "Suche Assistenz für Excel und cloud basierte Lösungen"
    results = extractor.extract_competences(text, "Assistenz")

    # 5. Validierung der Ergebnisse
    # Check Excel (Ebene 2)
    excel = next(r for r in results if r.original_term.lower() == "excel")
    assert excel.level == 2
    assert excel.original_term == "Excel"

    # Check Cloud (Ebene 4)
    cloud = next(r for r in results if "cloud" in r.original_term.lower())
    assert cloud.level == 4
    assert cloud.is_digital == True
    assert cloud.role_context == "Assistenz"
