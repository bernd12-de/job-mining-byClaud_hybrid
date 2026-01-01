from typing import BinaryIO, List, Dict, Set, Optional
from app.domain.models import AnalysisResultDTO, CompetenceDTO, Competence

class ICompetenceRepository(object):
    """Interface für die Hybrid-Kompetenz-Datenbank."""
    def get_all_skills(self) -> Set[str]: raise NotImplementedError
    def get_esco_only(self) -> Set[str]: raise NotImplementedError
    def get_custom_only(self) -> Set[str]: raise NotImplementedError
    def get_all_identifiable_labels(self) -> List[str]: raise NotImplementedError
    def get_level(self, term: str) -> int: raise NotImplementedError
    def is_digital_skill(self, term: str) -> bool: raise NotImplementedError

class ITextExtractor(object):
    def extract_text(self, file_stream: BinaryIO, filename: str) -> str:
        raise NotImplementedError

class ICompetenceExtractor(object):
    """
    Interface für die NLP-gestützte Kompetenzextraktion.
    FIX: Akzeptiert jetzt optional 'role', um den TypeError zu verhindern.
    """
    def extract_competences(self, text: str, role: str = None) -> List[CompetenceDTO]:
        raise NotImplementedError

class IJobMiningWorkflowManager(object):
    def run_full_analysis(self, file_stream: BinaryIO, filename: str) -> AnalysisResultDTO:
        raise NotImplementedError
    def run_analysis_from_scraped_text(self, cleaned_text: str, source_name: str) -> AnalysisResultDTO:
        raise NotImplementedError
