# core/entities/competence.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Competence:
    """Repräsentiert eine extrahierte und standardisierte Kompetenz."""

    original_skill: str
    esco_match: Optional[str]
    score: float
    category: str  # z.B. 'Skill', 'Knowledge', 'Attitude'
    context_section: str # z.B. 'Aufgaben', 'Anforderungen'
