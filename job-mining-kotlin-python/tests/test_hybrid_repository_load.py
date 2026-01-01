import requests


def test_hybrid_loads_from_kotlin(monkeypatch):
    sample = [
        {'original_term': 'Skill A', 'esco_uri': 'uri_a'},
        {'esco_label': 'Skill B', 'esco_uri': 'uri_b'}
    ]

    class FakeResponse:
        status_code = 200

        def json(self):
            return sample

    def fake_get(url, timeout=15):
        return FakeResponse()

    monkeypatch.setattr('requests.get', fake_get)

    # Create repository (constructor triggers _load_data)
    from app.infrastructure.repositories.hybrid_competence_repository import HybridCompetenceRepository

    repo = HybridCompetenceRepository(rule_client=None)

    assert len(repo.get_all_competences()) == 2
    assert 'Skill A' in repo.get_all_skills()
    assert 'Skill B' in repo.get_all_skills()
