"""
Domain Model: JobPosting (Entity)
Stellenanzeige mit allen Metadaten
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum

from .competence import Competence


class JobCategory(Enum):
    """UX-nahe Berufsfelder"""
    UX_UI_DESIGN = "UX/UI Design"
    PRODUCT_MANAGEMENT = "Product Management"
    BUSINESS_ANALYSIS = "Business Analysis"
    AGILE_COACHING = "Agile Coaching"
    UX_RESEARCH = "UX Research"
    FRONTEND_DEVELOPMENT = "Frontend Development"
    BACKEND_DEVELOPMENT = "Backend Development"
    DIGITAL_TRANSFORMATION = "Digital Transformation"
    OTHER = "Sonstige"


@dataclass
class JobPosting:
    """
    Entity: Stellenanzeige
    
    Hat Identity (id) - kann sich ändern (mutable)
    Enthält alle Metadaten: Firma, Ort, Jahr, Beruf
    """
    
    # Identity
    id: str
    
    # Dokument-Info
    file_name: str
    source: str
    raw_text: str
    file_type: str
    
    # Metadaten (WICHTIG!)
    job_title: Optional[str] = None              # Beruf, NICHT Skill!
    organization: Optional[str] = None            # Firma
    location: Optional[str] = None                # Ort
    year: Optional[int] = None                    # Jahr
    remote: Optional[bool] = None                 # Remote möglich?
    
    # NEU: Erweiterte Metadaten (Stufe 3)
    salary_min: Optional[int] = None              # Gehalt min (€/Jahr)
    salary_max: Optional[int] = None              # Gehalt max (€/Jahr)
    experience_years_min: Optional[int] = None    # Min. Erfahrung (Jahre)
    experience_years_max: Optional[int] = None    # Max. Erfahrung (Jahre)
    education_level: Optional[str] = None         # Bachelor, Master, PhD
    languages: dict = field(default_factory=dict) # {"Englisch": "C1", "Deutsch": "Muttersprache"}
    
    # Kategorisierung
    job_categories: List[JobCategory] = field(default_factory=list)
    
    # NEU: Aufgaben & Anforderungen
    tasks: List[str] = field(default_factory=list)              # Was wird gemacht?
    requirements: List[str] = field(default_factory=list)       # Was wird gebraucht?
    
    # Kompetenzen (Custom + ESCO)
    competences: List[Competence] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_competence(self, competence: Competence) -> None:
        """Füge Kompetenz hinzu (nur wenn noch nicht vorhanden)"""
        if competence not in self.competences:
            self.competences.append(competence)
            self.updated_at = datetime.now()
    
    def get_custom_competences(self) -> List[Competence]:
        """Nur Custom Skills"""
        return [c for c in self.competences if c.is_custom()]
    
    def get_esco_competences(self) -> List[Competence]:
        """Nur ESCO Skills"""
        return [c for c in self.competences if c.is_esco()]
    
    def get_competence_count(self) -> int:
        """Anzahl Skills"""
        return len(self.competences)
    
    def has_metadata(self) -> bool:
        """Sind Metadaten vorhanden?"""
        return bool(
            self.job_title or 
            self.organization or 
            self.location or 
            self.year
        )
    
    def get_metadata_completeness(self) -> float:
        """Metadaten-Vollständigkeit (0-1)"""
        fields = [self.job_title, self.organization, self.location, self.year]
        filled = sum(1 for f in fields if f is not None)
        return filled / len(fields)
