"""
models/competence.py
Competence Entity - Domain Model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from models.enums import CompetenceType


@dataclass
class Competence:
    """
    Einzelne Kompetenz nach ESCO/DigiBOKom
    
    Basierend auf:
    - ESCO Skill Taxonomy (Wilhelm-Weidner et al., 2025)
    - DigiBOKom Framework (Wiepcke, 2023)
    """
    
    # Identifikation
    name: str
    esco_uri: Optional[str] = None
    esco_code: Optional[str] = None
    
    # Klassifikation
    category: str = "General"
    competence_type: CompetenceType = CompetenceType.SKILL
    
    # Kontext
    context_snippet: Optional[str] = None
    confidence_score: float = 1.0
    
    # Alternative Bezeichnungen
    alternative_labels: List[str] = field(default_factory=list)
    
    # Metadaten
    source: str = "extraction"  # extraction, esco, manual, api
    domain: Optional[str] = None  # UX Design, Product Management, etc.
    extracted_at: datetime = field(default_factory=datetime.now)
    
    def __hash__(self):
        """Ermöglicht Verwendung in Sets"""
        return hash(self.name.lower())
    
    def __eq__(self, other):
        """Gleichheit basiert auf Name"""
        if not isinstance(other, Competence):
            return False
        return self.name.lower() == other.name.lower()
    
    def matches_text(self, text: str) -> bool:
        """Prüft ob Kompetenz im Text vorkommt (case-insensitive)"""
        text_lower = text.lower()
        
        # Hauptname
        if self.name.lower() in text_lower:
            return True
        
        # Alternative Labels
        for alt in self.alternative_labels:
            if alt.lower() in text_lower:
                return True
        
        return False
    
    def to_dict(self) -> dict:
        """Konvertiert zu Dictionary für Export"""
        return {
            'name': self.name,
            'category': self.category,
            'type': self.competence_type.value,
            'esco_uri': self.esco_uri,
            'alternative_labels': self.alternative_labels,
            'confidence': self.confidence_score,
            'source': self.source,
            'domain': self.domain
        }
