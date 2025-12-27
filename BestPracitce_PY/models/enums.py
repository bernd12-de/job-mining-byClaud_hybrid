"""
models/enums.py
Enumerations für das Domain Model
"""

from enum import Enum


class CompetenceType(Enum):
    """Kompetenztypen nach ESCO"""
    SKILL = "skill"
    KNOWLEDGE = "knowledge"
    ATTITUDE = "attitude"
    TOOL = "tool"
    METHOD = "method"
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    PLATFORM = "platform"


class JobCategory(Enum):
    """UX-nahe Berufsfelder"""
    UX_UI_DESIGN = "UX/UI Design"
    PRODUCT_MANAGEMENT = "Product Management"
    BUSINESS_ANALYSIS = "Business Analysis"
    AGILE_COACHING = "Agile Coaching"
    UX_RESEARCH = "UX Research"
    DEVELOPMENT = "Development"
    OTHER = "Sonstige"
