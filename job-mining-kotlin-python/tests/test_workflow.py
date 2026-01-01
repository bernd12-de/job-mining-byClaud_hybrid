import pytest
from unittest.mock import MagicMock
from app.application.job_mining_workflow_manager import JobMiningWorkflowManager

def test_complete_workflow_logic():
    mock_repo = MagicMock()
    mock_repo.get_all_identifiable_labels.return_value = ["Cloud Computing"]

    mock_service = MagicMock()
    mock_text_ext = MagicMock()
    mock_comp_ext = MagicMock()

    mock_metadata = MagicMock()
    # WICHTIG: Das Resultat muss ein echtes Dict sein, sonst knallt Pydantic
    mock_metadata.extract_all.return_value = {
        "job_title": "Assistenz",
        "location": "Berlin",
        "posting_date": "2024-01-01",
        "is_segmented": False
    }

    mock_service = MagicMock()
    mock_service.classify_industry.return_value = "Dienstleistung" # String!
    mock_service.classify_role.return_value = "Assistenz & Office" # String!

    manager = JobMiningWorkflowManager(
        text_extractor=MagicMock(),
        competence_extractor=MagicMock(),
        organization_service=mock_service,
        role_service=mock_service,
        metadata_extractor=mock_metadata
    )

    text = "Wir suchen eine Assistenz..."
    # FIX: Nutze die Methode, die im DirectoryProcessor verwendet wird (Punkt 9/10)
    # Falls die Methode im Manager 'process_job_ad' heißt, passe es hier an.
    result = manager._run_analysis_from_text(text, "test.pdf")
    assert result.job_role is not None
