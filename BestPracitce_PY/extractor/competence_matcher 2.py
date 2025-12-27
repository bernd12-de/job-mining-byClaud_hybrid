"""
services/competence_matcher.py
Matching-Logik für Kompetenzen im Text

WICHTIG: Enthält NUR Matching-Logik, KEINE Daten!
Nach: Single Responsibility Principle
"""

import re
import logging
from typing import List, Set
from models.competence import Competence


class CompetenceMatcher:
    """
    Matching-Engine für Kompetenzen
    
    Verantwortlichkeit: Findet Kompetenzen in Text
    
    Nach: Gharbi - "Single Responsibility"
    """
    
    def __init__(self, use_word_boundaries: bool = True, 
                 case_sensitive: bool = False,
                 minimum_confidence: float = 0.7):
        self.use_word_boundaries = use_word_boundaries
        self.case_sensitive = case_sensitive
        self.minimum_confidence = minimum_confidence
        self.logger = logging.getLogger(__name__)
    
    def find_matches(self, text: str, 
                    competence_library: List[Competence]) -> List[Competence]:
        """
        Findet alle Kompetenzen im Text
        
        Args:
            text: Zu durchsuchender Text
            competence_library: Liste aller verfügbaren Kompetenzen
        
        Returns:
            Liste gefundener Kompetenzen (dedupliziert)
        """
        if not text:
            return []
        
        found_competences = []
        found_names = set()  # Für Deduplizierung
        
        # Text vorbereiten
        search_text = text if self.case_sensitive else text.lower()
        
        for competence in competence_library:
            # Confidence-Filter
            if competence.confidence_score < self.minimum_confidence:
                continue
            
            # Hauptname prüfen
            if self._matches(competence.name, search_text):
                if competence.name.lower() not in found_names:
                    found_competences.append(competence)
                    found_names.add(competence.name.lower())
                continue
            
            # Alternative Labels prüfen
            for alt_label in competence.alternative_labels:
                if self._matches(alt_label, search_text):
                    if competence.name.lower() not in found_names:
                        found_competences.append(competence)
                        found_names.add(competence.name.lower())
                    break
        
        return found_competences
    
    def _matches(self, term: str, text: str) -> bool:
        """
        Prüft ob Term im Text vorkommt
        
        Mit Wortgrenzen für höhere Precision:
        "React" matched "React" aber nicht "Reaction"
        """
        search_term = term if self.case_sensitive else term.lower()
        
        if self.use_word_boundaries:
            # Wortgrenzen-Pattern
            pattern = r'\b' + re.escape(search_term) + r'\b'
            return bool(re.search(pattern, text))
        else:
            # Einfaches Substring-Matching
            return search_term in text
    
    def find_with_context(self, text: str, 
                         competence_library: List[Competence],
                         context_window: int = 50) -> List[tuple]:
        """
        Findet Kompetenzen MIT Kontext
        
        Returns:
            Liste von (Competence, context_snippet) Tuples
        """
        matches = []
        
        for competence in self.find_matches(text, competence_library):
            # Finde Position im Text
            context = self._extract_context(text, competence.name, context_window)
            matches.append((competence, context))
        
        return matches
    
    def _extract_context(self, text: str, term: str, window: int) -> str:
        """Extrahiert Textausschnitt um Term"""
        search_term = term if self.case_sensitive else term.lower()
        search_text = text if self.case_sensitive else text.lower()
        
        pattern = r'\b' + re.escape(search_term) + r'\b'
        match = re.search(pattern, search_text)
        
        if match:
            start = max(0, match.start() - window)
            end = min(len(text), match.end() + window)
            return text[start:end]
        
        return ""
    
    def get_statistics(self, text: str, 
                      competence_library: List[Competence]) -> dict:
        """Gibt Matching-Statistiken zurück"""
        found = self.find_matches(text, competence_library)
        
        from collections import Counter
        
        return {
            'total_found': len(found),
            'by_category': dict(Counter(c.category for c in found)),
            'by_type': dict(Counter(c.competence_type.value for c in found)),
            'by_domain': dict(Counter(c.domain for c in found if c.domain))
        }
