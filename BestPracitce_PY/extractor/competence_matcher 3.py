"""
Domain Extractor: Competence Matcher
Pattern Matching für Skills in Text
"""

import re
from typing import List, Tuple, Set
from domain.models.competence import Competence
from data.repositories.hybrid_competence_repository import HybridCompetenceRepository


class CompetenceMatcher:
    """
    Findet Kompetenzen in Text via Pattern Matching
    
    Features:
    - Word boundaries (\b) - verhindert False Positives
    - Case-insensitive
    - Alternative Labels
    - Deduplizierung
    """
    
    def __init__(self, competence_repo: HybridCompetenceRepository):
        self.repo = competence_repo
        self.all_skills = competence_repo.get_all()
        
        # Baue Pattern-Cache
        self._build_patterns()
    
    def _build_patterns(self) -> None:
        """Erstelle Regex-Patterns für alle Skills"""
        self.patterns = {}
        
        for skill in self.all_skills:
            # Alle Labels (name + alternatives)
            labels = skill.get_all_labels()
            
            # Erstelle Pattern für jedes Label
            for label in labels:
                # Escape special regex chars
                escaped = re.escape(label)
                
                # Word boundary pattern
                pattern = rf'\b{escaped}\b'
                
                # Speichere: Pattern -> Skill
                self.patterns[pattern] = skill
    
    def find_matches(self, text: str) -> List[Tuple[Competence, str]]:
        """
        Finde alle Skills in Text
        
        Returns:
            List[(Competence, context_snippet)]
        """
        matches = []
        seen: Set[str] = set()  # Deduplizierung
        
        for pattern, skill in self.patterns.items():
            # Case-insensitive search
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Skip wenn schon gefunden
                if skill.name in seen:
                    continue
                
                seen.add(skill.name)
                
                # Context snippet (50 chars vor/nach)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                matches.append((skill, context))
        
        return matches
    
    def filter_job_titles(
        self, 
        matches: List[Tuple[Competence, str]], 
        job_title: str
    ) -> List[Tuple[Competence, str]]:
        """
        Filtere Skills, die eigentlich Jobtitel sind
        
        z.B. "Product Owner" ist Beruf, nicht Skill!
        """
        if not job_title:
            return matches
        
        filtered = []
        job_title_lower = job_title.lower()
        
        for skill, context in matches:
            # Skip wenn Skill-Name im Jobtitel
            if skill.name.lower() in job_title_lower:
                continue
            
            filtered.append((skill, context))
        
        return filtered
    
    def get_statistics(self) -> dict:
        """Matching-Statistiken"""
        return {
            'total_patterns': len(self.patterns),
            'total_skills': len(self.all_skills),
            'custom_skills': len(self.repo.get_custom_only()),
            'esco_skills': len(self.repo.get_esco_only()),
        }
