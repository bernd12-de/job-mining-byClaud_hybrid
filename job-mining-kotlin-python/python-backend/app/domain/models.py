"""
Domain Layer: Konsolidierte Entitäten für die Job-Mining-Analyse
Architektur: Clean Architecture mit vollständiger Ebenen-Unterstützung (V2.0)
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date
from enum import Enum
import hashlib


class CompetenceType(Enum):
    """Typen von Kompetenzen nach ESCO"""
    SKILL = "skill"
    KNOWLEDGE = "knowledge"
    COMPETENCE = "competence"
    TOOL = "tool"
    METHOD = "method"
    CUSTOM = "custom"


class Competence(BaseModel):
    """
    Interne Repräsentation einer Kompetenz in der Wissensbasis (Repo).
    Basis für alle Matching-Operationen.
    """
    class Config:
        extra = "allow"

    preferred_label: str
    esco_uri: str
    alt_labels: List[str] = Field(default_factory=list)
    is_digital: bool = False  # NOT NULL mit Default False


class CompetenceDTO(BaseModel):
    """
    DTO für die Analyse-Pipeline.
    Verwendet bei der Extraktion und Übergabe zwischen Services.
    """
    id: Optional[int] = None
    original_term: str  # Der extrahierte Rohtext
    esco_label: Optional[str] = None  # Gematchtes ESCO-Label
    esco_uri: Optional[str] = None
    esco_group_code: Optional[str] = None
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    
    # Ebenen 1-5: Kompetenzstufen
    level: int = Field(default=2, ge=1, le=5)
    
    # Ebene 3: Digitale Skills
    is_digital: bool = False
    is_discovery: bool = False  # Ebene 1: Discovery-Phase
    
    # ESCO Collections
    collections: List[str] = Field(default_factory=list)
    
    # Ebene 4/5: Domänen und Quellen
    source_domain: Optional[str] = Field(default="System")
    
    # Ebene 6: Rollenkontext
    role_context: Optional[str] = None

    @validator('level', pre=True)
    def transform_level(cls, v):
        """Normalisiert Ebenen-Angaben (z.B. 'Ebene 4' -> 4)"""
        if isinstance(v, str):
            import re
            digits = re.findall(r'\d+', v)
            return int(digits[0]) if digits else 2
        return v


class AnalysisResultDTO(BaseModel):
    """
    DTO für das Analyse-Ergebnis.
    Wird zwischen Kotlin-API und Python-Backend ausgetauscht.
    """
    job_id: Optional[int] = None  # Wird von der DB generiert
    
    # Basis-Informationen
    title: str
    job_role: str
    region: str
    industry: str
    posting_date: str
    raw_text: str
    raw_text_hash: str  # SHA-256 für Duplikat-Erkennung
    
    # Status
    is_segmented: bool = False  # True wenn Aufgaben/Anforderungen getrennt
    source_url: Optional[str] = None  # Quelle für Web-Scraping (URLs)
    
    # Erkannte Kompetenzen
    competences: List[CompetenceDTO] = Field(default_factory=list)

    @classmethod
    def create_with_hash(cls, **data):
        """Zentraler Konstruktor: Generiert SHA-256 Hash automatisch"""
        if 'raw_text' in data and 'raw_text_hash' not in data:
            data['raw_text_hash'] = hashlib.sha256(
                data['raw_text'].encode('utf-8')
            ).hexdigest()
        return cls(**data)
