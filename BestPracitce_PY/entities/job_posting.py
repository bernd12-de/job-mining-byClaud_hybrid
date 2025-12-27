# core/entities/job_posting.py
from dataclasses import dataclass
from typing import List, Optional
from .competence import Competence

@dataclass
class JobPosting:
    """Repräsentiert eine vollständig verarbeitete Stellenanzeige."""

    source_id: str          # Eindeutige ID (z.B. Dateiname)
    source_path: str
    title: str
    company: str
    region: Optional[str]
    year: Optional[int]
    branch: Optional[str]
    raw_text: str           # Der gesamte extrahierte Text
    competences: List[Competence]
