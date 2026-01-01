"""
Test: Terminal Status Logging (Best Practice)

Testet das detaillierte Terminal-Feedback während der Analyse.
"""
import logging
import io
from app.application.job_mining_workflow_manager import JobMiningWorkflowManager
from app.infrastructure.extractor.metadata_extractor import MetadataExtractor
from app.infrastructure.extractor.competence_extractor import CompetenceExtractor
from app.infrastructure.repositories.hybrid_competence_repository import HybridCompetenceRepository
from app.application.services.organization_service import OrganizationService
from app.application.services.role_service import RoleService


def test_terminal_logging_metadata():
    """Test: Metadata Extraction Logging"""

    # Setup Logging Capture
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.INFO)
    logger = logging.getLogger("app.application.job_mining_workflow_manager")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Setup Components
    metadata_extractor = MetadataExtractor()
    repo = HybridCompetenceRepository()
    competence_extractor = CompetenceExtractor(repo)
    org_service = OrganizationService()
    role_service = RoleService()

    workflow = JobMiningWorkflowManager(
        text_extractor=None,  # Not needed for this test
        competence_extractor=competence_extractor,
        organization_service=org_service,
        role_service=role_service,
        metadata_extractor=metadata_extractor
    )

    # Test Text
    text = """
    BMW AG
    Senior Backend Developer (m/w/d)
    München
    Stand: Oktober 2024

    Wir suchen einen erfahrenen Java Developer.
    """

    # Execute
    try:
        workflow._execute_pipeline(text, source_name="test_bmw.pdf")
    except:
        pass  # Ignore errors, we just check logging

    # Get Log Output
    log_output = log_stream.getvalue()

    # Assertions
    assert "🚀 ANALYSE START:" in log_output, "Should log analysis start"
    assert "--- 🏢 METADATA EXTRACTION" in log_output, "Should log metadata section"
    assert "✓ Titel:" in log_output, "Should log extracted title"
    assert "✓ Firma:" in log_output, "Should log company name"
    assert "✓ Branch:" in log_output, "Should log branch/industry"
    assert "✓ Ort:" in log_output, "Should log location"
    assert "✓ Datum:" in log_output, "Should log posting date"
    assert "--- 🔍 COMPETENCE EXTRACTION" in log_output, "Should log competence section"
    assert "--- 📊 RESULT" in log_output, "Should log final result"

    print("✅ Terminal Logging Test bestanden")
    print("")
    print("Log Output:")
    print("=" * 60)
    print(log_output)
    print("=" * 60)


def test_terminal_logging_structure():
    """Test: Strukturiertes Logging Format"""

    # Setup
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    logger = logging.getLogger("app.application.job_mining_workflow_manager")
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    metadata_extractor = MetadataExtractor()
    repo = HybridCompetenceRepository()
    competence_extractor = CompetenceExtractor(repo)
    org_service = OrganizationService()
    role_service = RoleService()

    workflow = JobMiningWorkflowManager(
        text_extractor=None,
        competence_extractor=competence_extractor,
        organization_service=org_service,
        role_service=role_service,
        metadata_extractor=metadata_extractor
    )

    text = "SAP SE sucht Software Engineer in München. Stand: 2024"

    try:
        workflow._execute_pipeline(text, source_name="sap_job.pdf")
    except:
        pass

    log_output = log_stream.getvalue()

    # Check Symbols
    assert "🚀" in log_output, "Should use rocket emoji for start"
    assert "🏢" in log_output, "Should use building emoji for metadata"
    assert "🔍" in log_output, "Should use magnifier emoji for extraction"
    assert "📊" in log_output, "Should use chart emoji for results"
    assert "✓" in log_output or "✅" in log_output, "Should use checkmarks"

    print("✅ Strukturiertes Logging Format Test bestanden")


if __name__ == "__main__":
    print("=" * 60)
    print("TERMINAL LOGGING TESTS")
    print("=" * 60)
    print("")

    test_terminal_logging_metadata()
    test_terminal_logging_structure()

    print("")
    print("=" * 60)
    print("✅ ALLE TERMINAL LOGGING TESTS BESTANDEN")
    print("=" * 60)
