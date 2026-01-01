"""
Job-Klassifizierungen mit erweiterten Kategorien:
- Software Entwicklung (Frontend, Backend, Full-Stack)
- Data Science & Analytics
- Product Management (PO, PM)
- UX/UI Design
- Business/Consulting
- Finance
- HR/Operations

Basierend auf Job-Titel, Rolle und Industrie.
"""

import re
from typing import Optional, Dict, List


# ============================================================================
# JOB-KLASSIFIKATIONS-REGELN
# ============================================================================

ROLE_CLASSIFIERS = {
    'software_dev': {
        'keywords': r'(software|developer|programmier|engineer|backend|frontend|full.*stack|devops|architect)',
        'sub_categories': {
            'frontend': r'(frontend|react|vue|angular|typescript|javascript|ui.*develop)',
            'backend': r'(backend|server|api|python|java|kotlin|golang|rust)',
            'full_stack': r'(full.*stack|full-stack)',
            'devops': r'(devops|cloud|kubernetes|docker|infra)',
        }
    },
    'data_science': {
        'keywords': r'(data.*scientist|machine.*learning|data.*engineer|analytics|bi.*analyst|nlp|ai)',
        'sub_categories': {
            'ml_engineer': r'(machine.*learning|deep.*learning|model)',
            'data_engineer': r'(data.*engineer|etl|pipeline)',
            'analyst': r'(analyst|analytics|bi)',
        }
    },
    'product_management': {
        'keywords': r'(product.*owner|product.*manager|po|pm|scrum.*master|agile.*coach)',
        'sub_categories': {
            'po': r'(product.*owner|po\b)',
            'pm': r'(product.*manager|pm\b)',
            'scrum': r'(scrum.*master|agile.*coach)',
        }
    },
    'ux_design': {
        'keywords': r'(ux|ui|user.*experience|user.*interface|design|designer|interaction)',
        'sub_categories': {
            'ux': r'(ux|user.*experience|usability|research)',
            'ui': r'(ui|interface|visual.*design|figma)',
            'ux_ui': r'(ux.*ui|ui.*ux)',
        }
    },
    'consulting': {
        'keywords': r'(consultant|consulting|berater|beratung|strategy|transformation)',
        'sub_categories': {
            'digital': r'(digital|transformation|innovation)',
            'business': r'(business|strategy|management)',
            'tech': r'(tech.*consult|it.*consult)',
        }
    },
    'finance': {
        'keywords': r'(finance|fintech|banking|audit|accounting|accountant)',
        'sub_categories': {}
    },
    'hr_operations': {
        'keywords': r'(hr|human.*resource|recruitment|recruiting|operation)',
        'sub_categories': {}
    },
}


def classify_job_role(title: str, role: str = '', industry: str = '') -> Dict[str, str]:
    """
    Klassifiziert einen Job nach:
    - category: Hauptkategorie (software_dev, data_science, etc.)
    - sub_category: Unterkategorie (frontend, backend, etc.)
    - reason: Begründung
    
    Returns:
    {
        'category': 'software_dev',
        'sub_category': 'frontend',
        'reason': 'matched keywords in title'
    }
    """
    text = (title + ' ' + role + ' ' + industry).lower()
    
    # Durchsuche alle Kategorien
    for category, rules in ROLE_CLASSIFIERS.items():
        if re.search(rules['keywords'], text):
            # Finde Unterkategorie wenn vorhanden
            sub = 'general'
            for sub_cat, sub_pattern in rules.get('sub_categories', {}).items():
                if re.search(sub_pattern, text):
                    sub = sub_cat
                    break
            
            return {
                'category': category,
                'sub_category': sub,
                'reason': f'matched {category} keywords'
            }
    
    return {
        'category': 'unknown',
        'sub_category': 'unknown',
        'reason': 'no matching keywords'
    }


# ============================================================================
# KOMPETENZ-KATEGORISIERUNG (Eigenes Modell + ESCO)
# ============================================================================

COMPETENCE_CATEGORIES = {
    'technical_core': {
        'description': 'Programmiertechniken & Core-Sprachen',
        'keywords': r'(python|java|kotlin|javascript|typescript|go|rust|cpp|c#|ruby|php|sql|html|css)',
    },
    'frameworks_tools': {
        'description': 'Frameworks, Libraries, Tools',
        'keywords': r'(spring|django|fastapi|react|vue|angular|kubernetes|docker|git|terraform|aws|azure|gcp)',
    },
    'data_ml': {
        'description': 'Data & Machine Learning',
        'keywords': r'(pandas|numpy|scikit|tensorflow|pytorch|nlp|nlg|spacy|bert|transformer|feature engineering)',
    },
    'design_ux': {
        'description': 'Design & UX',
        'keywords': r'(figma|adobe|sketch|prototyp|wireframe|usability|user.*research|interaction)',
    },
    'product_management': {
        'description': 'Product & Business',
        'keywords': r'(scrum|kanban|agile|jira|confluence|roadmap|strategy|kpi|oas)',
    },
    'soft_skills': {
        'description': 'Soft Skills & Methoden',
        'keywords': r'(kommunikation|teamfähigkeit|leadership|presentation|projekt.*management|problem.*solving)',
    },
    'infrastructure': {
        'description': 'Infrastructure & DevOps',
        'keywords': r'(kubernetes|docker|aws|azure|gcp|terraform|ci.*cd|github|devops)',
    },
    'database': {
        'description': 'Datenbanken',
        'keywords': r'(sql|postgresql|mysql|mongodb|redis|elasticsearch|database)',
    },
    'languages': {
        'description': 'Sprachen',
        'keywords': r'(deutsch|englisch|französisch|spanisch|mandarin)',
    },
}


def categorize_competence(skill_name: str, collections: List[str] = None) -> Dict[str, str]:
    """
    Kategorisiert eine Kompetenz nach eigenem Modell.
    
    Returns:
    {
        'category': 'technical_core',
        'description': 'Programmiertechniken & Core-Sprachen',
        'source': 'custom_model'  # oder 'esco' wenn aus ESCO-Collection
    }
    """
    if not collections:
        collections = []
    
    text = skill_name.lower()
    
    # Priorisiere Custom-Kategorien
    for category, rules in COMPETENCE_CATEGORIES.items():
        if re.search(rules['keywords'], text):
            return {
                'category': category,
                'description': rules['description'],
                'source': 'custom_model'
            }
    
    # Fallback: Nutze ESCO-Collections falls vorhanden
    if 'digital' in collections:
        return {
            'category': 'technical_core',
            'description': 'ESCO Digital Skills',
            'source': 'esco'
        }
    elif 'research' in collections:
        return {
            'category': 'data_ml',
            'description': 'ESCO Research Skills',
            'source': 'esco'
        }
    elif 'transversal' in collections:
        return {
            'category': 'soft_skills',
            'description': 'ESCO Transversal Skills',
            'source': 'esco'
        }
    elif 'language' in collections:
        return {
            'category': 'languages',
            'description': 'ESCO Language Skills',
            'source': 'esco'
        }
    
    # Letzter Ausweg
    return {
        'category': 'other',
        'description': 'Uncategorized',
        'source': 'unknown'
    }


# ============================================================================
# REPORTING HELPERS
# ============================================================================

def group_jobs_by_category(jobs_data: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Gruppiert Jobs nach Jobkategorie.
    
    Input: Liste von Job-Daten aus summary/exports
    Output: {'software_dev': [...], 'ux_design': [...], ...}
    """
    grouped = {}
    
    for job in jobs_data:
        title = job.get('title', '')
        role = job.get('job_role', '')
        industry = job.get('industry', '')
        
        classification = classify_job_role(title, role, industry)
        category = classification['category']
        
        if category not in grouped:
            grouped[category] = []
        
        grouped[category].append({
            **job,
            'classification': classification
        })
    
    return grouped


def group_skills_by_category(skills_with_metadata: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Gruppiert Skills nach Kompetenz-Kategorie.
    
    Input: Liste von {'name': 'Python', 'count': 12, 'collections': [...]}
    Output: {'technical_core': [...], 'frameworks_tools': [...], ...}
    """
    grouped = {}
    
    for skill in skills_with_metadata:
        name = skill.get('name', '')
        collections = skill.get('collections', [])
        
        categorization = categorize_competence(name, collections)
        category = categorization['category']
        
        if category not in grouped:
            grouped[category] = []
        
        grouped[category].append({
            **skill,
            'categorization': categorization
        })
    
    return grouped
