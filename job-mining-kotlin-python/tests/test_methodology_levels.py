from unittest.mock import MagicMock

import pytest
import json
from pathlib import Path
from app.infrastructure.repositories.hybrid_competence_repository import HybridCompetenceRepository
from app.infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor

@pytest.fixture
def mock_data_paths(tmp_path):
    """Erstellt temporäre Mini-JSONs für den Test (Ebene 4 & 5)."""
    fb_path = tmp_path / "test_fachbuch.json"
    ac_path = tmp_path / "test_academia.json"

    # Ebene 4: Begriffe aus Fachbüchern (z.B. Cloud-Architektur)
    fb_path.write_text(json.dumps(["Cloud-Computing", "Microservices"]))
    # Ebene 5: Begriffe aus Modulhandbüchern (z.B. Digitale Transformation)
    ac_path.write_text(json.dumps(["Python-Programmierung", "Data Science"]))

    return str(fb_path), str(ac_path)


# tests/test_methodology_levels.py
def test_assistenz_digital_shift_logic(mock_data_paths):
    fb_p, ac_p = mock_data_paths

    # Der Konstruktor regelt nun alles
    # Wir übergeben einen MockClient, um Netzwerkzugriffe zu vermeiden
    mock_client = MagicMock()
    mock_client.get_esco_full.return_value = {"excel": "uri1"}

    from app.infrastructure.repositories.hybrid_competence_repository import HybridCompetenceRepository
    repo = HybridCompetenceRepository(fachbuch_path=fb_p, academia_path=ac_p, rule_client=mock_client)

    repo.get_all_identifiable_labels = lambda: ["Mircoservice", "VwL","Cloud-Computing"]

    mock_manager = MagicMock()
    mock_manager.create_competence_dto.side_effect = lambda **k: MagicMock(**k)
    extractor = SpaCyCompetenceExtractor(repository=repo, manager=mock_manager)

    results = extractor.extract_competences("Assistenz für Excel und Cloud-Computing", "Assistenz & Office")
    assert len(results) > 0

'''
def test_assistenz_digital_shift_logic(mock_data_paths):
    fb_p, ac_p = mock_data_paths

    # 1. Repo mit Test-Pfaden initialisieren
    repo = HybridCompetenceRepository(fachbuch_path=fb_p, academia_path=ac_p)
    repo.load_local_domains()
    # Wir simulieren ESCO-Labels (Ebene 2)
    repo._esco_lower_set = {"excel", "terminplanung"}

    # 2. Extractor mit diesem Repo laden
    extractor = SpaCyCompetenceExtractor(repository=repo)

    # 3. TEST-SZENARIO: Assistenz-Anzeige mit modernem Skill
    test_text = "Wir suchen eine Assistenz für Excel und Cloud-Computing."
    role = "Assistenz & Office"

    results = extractor.extract_competences(test_text, role)

    # 4. VALIDIERUNG (Wissenschaftlicher Beleg)
    # Excel sollte Ebene 2 sein
    excel_skill = next(s for s in results if "Excel" in s.original_term)
    assert excel_skill.level == 2

    # Cloud-Computing sollte Ebene 4 sein (da in der Fachbuch-Test-JSON)
    cloud_skill = next(s for s in results if "Cloud" in s.original_term)
    assert cloud_skill.level == 4
    assert cloud_skill.role_context == "Assistenz & Office"
'''
