import pytest
import inspect
from unittest.mock import MagicMock
from app.infrastructure.repositories.hybrid_competence_repository import HybridCompetenceRepository
from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
from app.domain.models import CompetenceDTO, AnalysisResultDTO

def test_repository_client_init_contract():
    """
    KI-SCHUTZ: Prüft, ob das Repository den Client mit Parametern aufruft,
    die der Client tatsächlich unterstützt. Verhindert TypeError: unexpected keyword argument 'base_url'.
    """
    # 1. Analysiere die __init__ von KotlinRuleClient
    client_params = inspect.signature(KotlinRuleClient.__init__).parameters

    # 2. Prüfe den Quellcode der Repository-Initialisierung
    repo_init_source = inspect.getsource(HybridCompetenceRepository.__init__)

    # Der Fehlerfall: Repository reicht 'base_url' durch, aber Client hat es nicht
    if "base_url" not in client_params and "kwargs" not in client_params:
        assert "base_url=" not in repo_init_source, (
            "🚨 KRITISCHER ARCHITEKTUR-FEHLER: Das Repository versucht 'base_url' an den Client "
            "durchzureichen, aber der KotlinRuleClient akzeptiert diesen Parameter nicht!"
        )

def test_repository_interface_stability():
    """
    Stellt sicher, dass lebenswichtige Methoden für den Extractor existieren.
    Egal wie die Variablen intern heißen (custom_domains vs fachbuch_skills).
    """
    repo = HybridCompetenceRepository(rule_client=MagicMock())

    # Der 'Vertrag' mit dem SpaCyCompetenceExtractor
    assert hasattr(repo, 'get_all_identifiable_labels'), "🚨 VERTRAGSBRUCH: Methode get_all_identifiable_labels fehlt!"
    assert hasattr(repo, 'get_level'), "🚨 VERTRAGSBRUCH: Methode get_level fehlt!"
    assert hasattr(repo, 'is_digital_skill'), "🚨 VERTRAGSBRUCH: Methode is_digital_skill fehlt!"

def test_pydantic_dto_contract():
    """
    Prüft, ob die DTO-Modelle stabil gegen 'KI-Naming-Chaos' sind.
    """
    # Teste CompetenceDTO
    comp_fields = CompetenceDTO.model_fields.keys()
    required = ["original_term", "level", "esco_uri"]
    for field in required:
        assert field in comp_fields, f"🚨 VERTRAGSBRUCH: Pflichtfeld '{field}' im CompetenceDTO verschwunden!"

    # Teste AnalysisResultDTO (Wichtig für Workflow)
    analysis_fields = AnalysisResultDTO.model_fields.keys()
    assert "job_role" in analysis_fields
    assert "industry" in analysis_fields

def test_workflow_manager_dependency_injection():
    """
    Stellt sicher, dass der WorkflowManager alle Services erhält, die er zum
    Überleben braucht.
    """
    from app.application.job_mining_workflow_manager import JobMiningWorkflowManager

    sig = inspect.signature(JobMiningWorkflowManager.__init__)
    params = sig.parameters.keys()

    # Diese 5 müssen vorhanden sein, sonst bricht der Prozess ab
    required = ['text_extractor', 'competence_extractor', 'organization_service', 'role_service', 'metadata_extractor']
    for p in required:
        assert p in params, f"🚨 FEHLENDE ABHÄNGIGKEIT: WorkflowManager braucht '{p}' im Konstruktor!"

@pytest.mark.asyncio
async def test_kotlin_bridge_port_readiness():
    """
    Prüft theoretisch, ob der Client für einen Port-Check bereit ist.
    """
    client = KotlinRuleClient()
    assert hasattr(client, 'base_url'), "Client hat keine Basis-URL konfiguriert."
    assert "http" in client.base_url, "Ungültiges URL-Format im Client."
