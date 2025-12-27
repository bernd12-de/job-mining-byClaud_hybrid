"""
Domain Model: Competence (Value Object)
Unveränderliches Kompetenzobjekt - kann Custom ODER ESCO sein
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class CompetenceSource(Enum):
    """Herkunft der Kompetenz"""
    CUSTOM = "custom"       # Eigene Skills-Liste
    ESCO = "esco"           # ESCO-Taxonomie
    HYBRID = "hybrid"       # In beiden vorhanden


class CompetenceType(Enum):
    """ESCO-konforme Kompetenz-Typen"""
    SKILL = "skill"
    KNOWLEDGE = "knowledge"
    TOOL = "tool"
    TECHNOLOGY = "technology"
    METHOD = "method"
    FRAMEWORK = "framework"
    PLATFORM = "platform"
    STANDARD = "standard"
    CONCEPT = "concept"
    SOFT_SKILL = "soft_skill"
    LANGUAGE = "language"
    CERTIFICATION = "certification"


@dataclass(frozen=True)
class Competence:
    """
    Value Object: Kompetenz
    
    Immutable (frozen=True) - keine Änderung nach Erstellung!
    Zweigleisig: Custom + ESCO kombiniert
    """
    
    # Basis
    name: str
    category: str
    competence_type: CompetenceType
    source: CompetenceSource
    
    # Optional: ESCO-Daten
    esco_uri: Optional[str] = None
    esco_code: Optional[str] = None
    
    # Optional: Metadaten
    alternative_labels: List[str] = None
    confidence_score: float = 1.0
    context_snippet: Optional[str] = None
    
    def __post_init__(self):
        """Validierung nach Erstellung"""
        if self.alternative_labels is None:
            object.__setattr__(self, 'alternative_labels', [])
        
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError(f"Confidence must be 0-1, got {self.confidence_score}")
    
    def is_esco(self) -> bool:
        """Ist dies eine ESCO-Kompetenz?"""
        return self.source in [CompetenceSource.ESCO, CompetenceSource.HYBRID]
    
    def is_custom(self) -> bool:
        """Ist dies eine Custom-Kompetenz?"""
        return self.source in [CompetenceSource.CUSTOM, CompetenceSource.HYBRID]
    
    def get_all_labels(self) -> List[str]:
        """Alle Labels (name + alternatives)"""
        return [self.name] + self.alternative_labels
