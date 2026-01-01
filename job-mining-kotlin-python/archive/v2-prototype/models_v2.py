"""
NEUE ARCHITEKTUR V2.0: Core Domain Models
Konsolidierte, fehlerfreie Datenmodelle mit Clean Architecture
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import date, datetime
from enum import Enum


# ============================================================================
# ENUMS FÜR TYPSICHERHEIT
# ============================================================================

class CompetenceType(Enum):
    """Typ der Kompetenz"""
    SKILL = "skill"           # ESCO Skills
    TOOL = "tool"             # Software/Tools
    METHOD = "method"         # Methoden (Agile, SCRUM)
    LANGUAGE = "language"     # Sprachen
    CERTIFICATION = "cert"    # Zertifizierungen
    CUSTOM = "custom"         # Custom/Business


# ============================================================================
# CORE DOMAIN MODELS
# ============================================================================

@dataclass(frozen=True)
class Competence:
    """
    Standardisierte ESCO-basierte Kompetenz.
    Immutable für sichere Datenverwaltung.
    """
    # Kern-Identifikation
    name: str                           # Klartext-Label (z.B. 'User Experience Design')
    esco_uri: Optional[str] = None      # ESCO-URI oder Custom-ID
    
    # Kategorisierung
    category: Optional[str] = None      # Kategorie (z.B. 'UX Tools', 'Agile Method')
    domain: Optional[str] = None        # Domäne (z.B. 'UX', 'ICT', 'Finance')
    competence_type: CompetenceType = CompetenceType.SKILL
    
    # Matching-Metadaten (7-Ebenen-Modell)
    confidence: float = 1.0             # Fuzzy-Matching-Konfidenz (0-1)
    source_match: Optional[str] = None  # Original-String, der gematcht hat
    source_section: Optional[str] = None # 'requirements', 'tasks', etc.
    
    # Level & Digital (Ebene 2, 3)
    level: Optional[int] = None         # ESCO Level (1-8)
    is_digital: bool = False            # Digital Skill? (Ebene 3)
    
    # Kontext (Ebene 6)
    role_context: Optional[str] = None  # Job-Rolle für Kontextualisierung
    
    def __hash__(self):
        return hash(self.name.lower())
    
    def __eq__(self, other):
        if not isinstance(other, Competence):
            return False
        return self.name.lower() == other.name.lower()


@dataclass
class JobPosting:
    """
    Die zentrale Entität für eine Stellenanzeige.
    Mit allen Ebenen des 7-Ebenen-Modells.
    """
    # ===== 1. IDENTIFIKATION & ROHDATEN =====
    job_id: str                         # Eindeutige ID
    source_path: str                    # Pfad zur Original-Datei
    raw_text: str                       # Original-Volltext
    cleaned_text: str = ""              # Vorbereitet für Matching
    
    # ===== 2. BASIS-METADATEN =====
    title: Optional[str] = None         # Jobtitel
    company: Optional[str] = None       # Unternehmen
    location: Optional[str] = None      # Ort (Remote/Stadt)
    
    # ===== KRITISCH: ZEITREIHEN-ANALYSE =====
    year: Optional[int] = None          # Veröffentlichungsjahr (für Trend-Analyse)
    date_parsed: Optional[date] = None  # Vollständiges Datum
    
    # ===== 3. SEGMENTIERUNG (Ebene 6) =====
    is_segmented: bool = False          # Erfolgreich segmentiert?
    tasks_text: Optional[str] = None    # Extrahierte Aufgaben
    requirements_text: Optional[str] = None # Extrahierte Anforderungen
    
    # ===== 4-5. DOMAIN-INFERENZ =====
    inferred_level: Optional[int] = None # Inferiertes Level (2=Job, 4=Buch, 5=Academia)
    source_domain: str = "Job Posting"  # 'Job Posting' | 'Fachbuch' | 'Academia'
    
    # ===== KOMPETENZEN & ANALYSE =====
    competences: List[Competence] = field(default_factory=list)
    
    # ===== QUALITÄTS-METRIKEN =====
    processing_timestamp: datetime = field(default_factory=datetime.now)
    extraction_quality_score: float = 0.0  # 0-1 Qualitätsscore
    
    # ===== OPTIONALE STUFE 3 METADATEN =====
    salary_min: Optional[int] = None    # Mindestgehalt
    salary_max: Optional[int] = None    # Maximalgehalt
    experience_years: Optional[int] = None # Geforderte Jahre Erfahrung
    education_level: Optional[str] = None # z.B. 'Bachelor', 'Master'
    languages: List[str] = field(default_factory=list) # Geforderte Sprachen
    
    def __hash__(self):
        return hash(self.job_id)
    
    def add_competence(self, competence: Competence):
        """Füge Kompetenz hinzu mit Deduplizierung."""
        if competence not in self.competences:
            self.competences.append(competence)
    
    def get_competences_by_domain(self, domain: str) -> List[Competence]:
        """Filtere Kompetenzen nach Domäne."""
        return [c for c in self.competences if c.domain == domain]
    
    def get_high_confidence_competences(self, threshold: float = 0.85) -> List[Competence]:
        """Nur hochwertige Matches."""
        return [c for c in self.competences if c.confidence >= threshold]


# ============================================================================
# AGGREGATE TYPES (für spätere Use Cases)
# ============================================================================

@dataclass
class CompetenceTimeSeries:
    """Zeitreihe von Kompetenz-Vorkommen für Trendanalyse"""
    competence: Competence
    years: Dict[int, int] = field(default_factory=dict)  # {2020: 15, 2021: 23, ...}
    
    def add_occurrence(self, year: int):
        """Registriere ein Vorkommen in diesem Jahr."""
        self.years[year] = self.years.get(year, 0) + 1
    
    def trend(self) -> str:
        """Trend berechnen: 'rising', 'falling', 'stable'"""
        if len(self.years) < 2:
            return 'unknown'
        sorted_years = sorted(self.years.items())
        first_val = sorted_years[0][1]
        last_val = sorted_years[-1][1]
        if last_val > first_val * 1.2:
            return 'rising'
        elif last_val < first_val * 0.8:
            return 'falling'
        return 'stable'


@dataclass
class AnalysisResult:
    """Ergebnis einer Job-Analyse"""
    job_posting: JobPosting
    extracted_competences: List[Competence]
    confidence_average: float
    error_count: int = 0
    error_messages: List[str] = field(default_factory=list)
    
    def is_successful(self) -> bool:
        """War die Analyse erfolgreich?"""
        return self.error_count == 0 and len(self.extracted_competences) > 0
