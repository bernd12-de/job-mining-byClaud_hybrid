import os
import json
import shutil
from app.infrastructure.repositories.hybrid_competence_repository import HybridCompetenceRepository
from app.domain.models import Competence


def setup_test_domains(tmp_dir):
    d = os.path.join(tmp_dir, 'data', 'job_domains')
    os.makedirs(d, exist_ok=True)
    academia = {
        "domain": "test_academia",
        "level": 5,
        "competences": [{"name": "Quantentheorie", "level": 5}]
    }
    fachbuch = {
        "domain": "test_fachbuch",
        "level": 4,
        "competences": [{"name": "Microservices", "level": 4}]
    }
    with open(os.path.join(d, 'test_academia.json'), 'w', encoding='utf-8') as f:
        json.dump(academia, f, ensure_ascii=False)
    with open(os.path.join(d, 'test_fachbuch.json'), 'w', encoding='utf-8') as f:
        json.dump(fachbuch, f, ensure_ascii=False)
    return d


def test_get_level_priority(tmp_path, monkeypatch):
    root = tmp_path
    # copy an empty data tree
    (root / 'data').mkdir()
    # create job_domains
    jd = setup_test_domains(str(root))

    # monkeypatch cwd path resolution inside repository by setting CWD
    monkeypatch.chdir(str(root))

    repo = HybridCompetenceRepository(rule_client=None)

    # reload local domains and sync sets
    repo._load_local_domains_v2()
    repo._sync_legacy_sets()

    assert repo.get_level('Quantentheorie') == 5
    assert repo.get_level('Microservices') == 4


def test_is_digital_skill_and_esco_index(tmp_path, monkeypatch):
    # Prepare repo with one Competence in _all_competences
    repo = HybridCompetenceRepository(rule_client=None)
    comp = Competence(preferred_label='Jira', esco_uri='http://example/1')
    # attach metadata on object (simulated source)
    setattr(comp, 'is_digital', True)
    setattr(comp, 'level', 2)

    repo._all_competences.append(comp)
    repo._build_esco_index()

    assert repo.is_known('Jira') is True
    assert repo.is_digital_skill('Jira') is True
    assert repo.get_level('Jira') == 3  # Digital Skills = Level 3


def test_digital_skill_keyword_heuristic():
    """Test: Digital Skill Erkennung über Keywords"""
    repo = HybridCompetenceRepository(rule_client=None)
    
    # Keywords sollten erkannt werden
    assert repo.is_digital_skill("Python Programmierung") == True
    assert repo.is_digital_skill("Machine Learning Modelle") == True
    assert repo.is_digital_skill("Cloud Computing AWS") == True
    assert repo.is_digital_skill("SAP ERP System") == True
    assert repo.is_digital_skill("JavaScript Framework") == True
    assert repo.is_digital_skill("Data Science") == True
    
    # Nicht-digitale Skills
    assert repo.is_digital_skill("Teamarbeit") == False
    assert repo.is_digital_skill("Kommunikationsfähigkeit") == False
    assert repo.is_digital_skill("Führungskompetenz") == False


def test_level_hierarchy_with_digital_flag(tmp_path, monkeypatch):
    """Test: Level-Hierarchie Academia > Fachbuch > ESCO Digital > ESCO Standard"""
    root = tmp_path
    (root / 'data').mkdir()
    setup_test_domains(str(root))
    monkeypatch.chdir(str(root))
    
    repo = HybridCompetenceRepository(rule_client=None)
    repo._load_local_domains_v2()
    repo._sync_legacy_sets()
    
    # Academia = Level 5
    assert repo.get_level('Quantentheorie') == 5
    
    # Fachbuch = Level 4
    assert repo.get_level('Microservices') == 4
    
    # ESCO Digital = Level 3
    comp_digital = Competence(preferred_label='Python', esco_uri='http://example/py')
    setattr(comp_digital, 'is_digital', True)
    setattr(comp_digital, 'level', 2)
    repo._all_competences.append(comp_digital)
    repo._build_esco_index()
    assert repo.get_level('Python') == 3
    
    # ESCO Standard = Level 2
    comp_standard = Competence(preferred_label='Teamarbeit', esco_uri='http://example/team')
    setattr(comp_standard, 'is_digital', False)
    setattr(comp_standard, 'level', 2)
    repo._all_competences.append(comp_standard)
    repo._build_esco_index()
    assert repo.get_level('Teamarbeit') == 2


def test_unknown_skill_default_level():
    """Test: Unbekannte Skills bekommen Default Level 2"""
    repo = HybridCompetenceRepository(rule_client=None)
    
    level = repo.get_level("völlig unbekannter skill xyz123")
    assert level == 2
