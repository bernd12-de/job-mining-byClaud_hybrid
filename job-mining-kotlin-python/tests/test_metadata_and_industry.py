import pytest

from app.infrastructure.extractor.metadata_extractor import MetadataExtractor
from app.application.services.organization_service import OrganizationService
from app.application.services.role_service import RoleService


class _DummyRuleClient:
    def fetch_industry_mappings(self):
        return {}

    def fetch_role_mappings(self):
        return {}


def test_section_filter_removes_benefits_from_processing_text():
    extractor = MetadataExtractor()
    text = (
        "Job Titel\n"
        "DEINE AUFGABEN:\n"
        "Plane Features und entwickle robuste APIs. Baue Schnittstellen, orchestriere Services, dokumentiere sauber.\n"
        "DEIN PROFIL:\n"
        "Erfahrung in Python, FastAPI, AWS, Docker, CI/CD und Monitoring werden vorausgesetzt.\n"
        "WIR BIETEN:\n"
        "Obstkiste und Kicker im Büro."
    )

    meta = extractor.extract_all(text, filename="testfile.txt")

    assert "Obstkiste" not in meta.get("processing_text", ""), "Benefits sollten aus dem Analysetext entfernt sein"
    assert meta.get("is_segmented") is True
    assert "Python" in meta.get("processing_text", ""), "Relevante Profil-Inhalte müssen erhalten bleiben"


def test_heuristic_industry_fallback():
    service = OrganizationService(rule_client=_DummyRuleClient())
    text = "Wir betreiben eine Logistik Plattform mit Supply Chain Optimierung und Transportsteuerung."

    detected = service.detect_industry(text)

    assert detected in ("Logistik & Mobilität", "Logistik & Mobilitaet")


def test_role_fallback_mapping():
    service = RoleService(rule_client=_DummyRuleClient())
    text = "Wir suchen einen Software Developer der skalierbare Services baut."

    detected = service.classify_role(job_text=text, job_title="Senior Software Engineer")

    assert detected == "Software Engineer"


def test_remote_location_detection():
    extractor = MetadataExtractor()
    text = "Senior Backend Engineer (Remote) – du kannst 100% im Homeoffice arbeiten."

    meta = extractor.extract_all(text, filename="remote.txt")

    assert meta.get("region") == "Remote"
