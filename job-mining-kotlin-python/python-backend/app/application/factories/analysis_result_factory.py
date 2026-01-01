import hashlib
import logging
from typing import List, Optional
from app.domain.models import AnalysisResultDTO, CompetenceDTO

logger = logging.getLogger(__name__)

class AnalysisResultFactory:
    """
    Zentrale Factory (SSoT) für die Erstellung von DTOs.
    Löst die Abhängigkeit zwischen Manager und Extractor auf.
    """

    @staticmethod
    def create_competence(
            original_term: str,
            esco_label: str,
            esco_uri: str,
            level: int,
            esco_group_code: Optional[str] = None,
            is_digital: bool = False,
            is_discovery: bool = False,
            collections: Optional[List[str]] = None,
            role_context: Optional[str] = None,
            confidence: float = 1.0
    ) -> CompetenceDTO:
        """Erstellt ein valides CompetenceDTO für den Extractor."""
        return CompetenceDTO(
            original_term=original_term,
            esco_label=esco_label,
            esco_uri=esco_uri,
            esco_group_code=esco_group_code,
            level=level,
            is_digital=is_digital,
            is_discovery=is_discovery,
            collections=collections or [],
            role_context=role_context,
            confidence_score=confidence
        )

    @staticmethod
    def create_result(
            title: str,
            job_role: str,
            industry: str,
            raw_text: str,
            competences: List[CompetenceDTO],
            posting_date: str = "2024-12-01",
            region: str = "Unbekannt",
            is_segmented: bool = False,
            source_url: Optional[str] = None,
            raw_text_hash: Optional[str] = None
    ) -> AnalysisResultDTO:
        """Baut das finale AnalysisResultDTO für die Datenbank/Kotlin."""

        # 1. Hash berechnen falls nicht da (Idempotenz)
        if not raw_text_hash:
            raw_text_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()

        # 2. DTO bauen (Passend zu models.py!)
        return AnalysisResultDTO(
            job_id=None,
            title=title,
            job_role=job_role,      # FIX: Hieß vorher detected_role
            region=region,
            industry=industry,
            posting_date=posting_date,
            raw_text=raw_text,
            raw_text_hash=raw_text_hash,
            is_segmented=is_segmented,
            source_url=source_url,
            competences=competences
        )
