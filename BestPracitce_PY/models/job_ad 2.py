
# HINWEIS: Dies ist eine VEREINFACHTE Version
# Vollständiger Code verfügbar im Chat-Verlauf

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class CompetenceType(Enum):
    SKILL = "skill"
    TOOL = "tool"
    TECHNOLOGY = "technology"
    METHOD = "method"
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    PLATFORM = "platform"

class JobCategory(Enum):
    UX_UI_DESIGN = "UX/UI Design"
    PRODUCT_MANAGEMENT = "Product Management"
    BUSINESS_ANALYSIS = "Business Analysis"
    AGILE_COACHING = "Agile Coaching"
    UX_RESEARCH = "UX Research"
    DEVELOPMENT = "Development"
    OTHER = "Other"

@dataclass
class Organization:
    name: str = "Unbekannt"
    branch: Optional[str] = None

@dataclass
class Competence:
    name: str
    category: str = "General"
    competence_type: CompetenceType = CompetenceType.SKILL
    esco_uri: str = ""
    alternative_labels: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    source: str = "extracted"
    context_snippet: Optional[str] = None

@dataclass
class Requirements:
    education_level: Optional[str] = None
    years_experience: Optional[int] = None
    languages: Dict[str, str] = field(default_factory=dict)
    soft_skills: List[str] = field(default_factory=list)

@dataclass
class JobAd:
    id: str
    file_name: str
    source: str
    raw_text: str
    char_count: int = 0
    word_count: int = 0

    job_title: str = "Unbekannt"
    organization: Optional[Organization] = None
    location: str = "Nicht angegeben"
    remote_option: Optional[str] = None

    competences: List[Competence] = field(default_factory=list)
    job_categories: List[JobCategory] = field(default_factory=list)
    requirements: Optional[Requirements] = None

    posting_date: Optional[datetime] = None
    collection_date: Optional[datetime] = None
    year: Optional[int] = None
    month: Optional[int] = None
    quarter: Optional[str] = None

    cleaned_text: Optional[str] = None
    text_quality: float = 0.0
    extraction_quality: float = 0.0

    def has_competence(self, competence_name: str) -> bool:
        return any(c.name.lower() == competence_name.lower() for c in self.competences)

    def get_time_period(self) -> str:
        if self.quarter:
            return self.quarter
        elif self.year and self.month:
            return f"{self.year}-{self.month:02d}"
        elif self.year:
            return str(self.year)
        return "Unknown"

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'file_name': self.file_name,
            'source': self.source,
            'job_title': self.job_title,
            'company_name': self.organization.name if self.organization else None,
            'company_branch': self.organization.branch if self.organization else None,
            'location': self.location,
            'remote_option': self.remote_option,
            'posting_date': self.posting_date.isoformat() if self.posting_date else None,
            'year': self.year,
            'month': self.month,
            'quarter': self.quarter,
            'job_categories': [cat.value for cat in self.job_categories],
            'competences_count': len(self.competences),
            'competences': [
                {
                    'name': c.name,
                    'category': c.category,
                    'type': c.competence_type.value,
                    'esco_uri': c.esco_uri
                }
                for c in self.competences
            ],
            'char_count': self.char_count,
            'word_count': self.word_count,
            'text_quality': self.text_quality,
            'extraction_quality': self.extraction_quality
        }

@dataclass
class CompetenceCluster:
    id: str
    name: str
    description: str
    competences: List[Competence] = field(default_factory=list)
    job_ads_count: int = 0
