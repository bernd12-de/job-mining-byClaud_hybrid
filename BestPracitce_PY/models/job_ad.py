from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import datetime

class CompetenceType(Enum):
    TOOL = "tool"
    METHOD = "method"
    FRAMEWORK = "framework"
    LANGUAGE = "language"
    PLATFORM = "platform"
    KNOWLEDGE = "knowledge"
    ATTITUDE = "attitude"
    SKILL = "skill"
    TECHNOLOGY = "technology"

class JobCategory(Enum):
    UX_DESIGN = "UX Design"
    UI_DESIGN = "UI Design"
    CONSULTING = "Consulting"
    WORKING_STUDENT = "Working Student"
    OTHER = "Other"

@dataclass
class Competence:
    name: str
    category: str = "General"
    competence_type: CompetenceType = CompetenceType.SKILL
    esco_uri: str = ""
    alternative_labels: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    source: str = "library_rule"
    context_snippet: str = ""

@dataclass
class Organization:
    name: str = "Unbekannt"
    branch: str = "Unknown"
    website: str = ""

@dataclass
class JobAd:
    id: str
    file_name: str
    source: str
    raw_text: str
    char_count: int
    word_count: int
    collection_date: datetime
    cleaned_text: str = ""
    text_quality: float = 0.0
    job_title: str = "Unbekannt"
    job_categories: List[JobCategory] = field(default_factory=list)
    organization: Optional[Organization] = None
    location: str = "Nicht angegeben"
    posting_date: Optional[datetime] = None
    competences: List[Competence] = field(default_factory=list)
    competences_count: int = 0
    extraction_quality: float = 0.0

    def get_time_period(self) -> str:
        dt = self.posting_date or self.collection_date
        return f"{dt.year}-Q{((dt.month-1)//3)+1}"

    def has_competence(self, name: str) -> bool:
        return any(c.name == name for c in self.competences)

    def to_dict(self):
        return {
            "id": self.id,
            "file_name": self.file_name,
            "source": self.source,
            "date_processed": self.collection_date.isoformat(),
            "posting_date": self.posting_date.isoformat() if self.posting_date else "",
            "year": (self.posting_date or self.collection_date).year,
            "month": (self.posting_date or self.collection_date).month,
            "quarter": self.get_time_period(),
            "job_title": self.job_title,
            "company_name": self.organization.name if self.organization else "Unbekannt",
            "company_branch": self.organization.branch if self.organization else "Unknown",
            "location": self.location,
            "job_categories": [c.value for c in self.job_categories],
            "competences_count": self.competences_count,
            "competences": [c.__dict__ | {"competence_type": c.competence_type.value} for c in self.competences],
            "char_count": self.char_count,
            "word_count": self.word_count,
            "extraction_quality": self.extraction_quality,
        }
