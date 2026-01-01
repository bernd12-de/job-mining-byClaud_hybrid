"""
Application Layer: Competence-Matching Service
Orchestriert die Kompetenzen-Extraktion mit Fuzzy-Matching-Strategie
"""
from typing import List, Set, Optional, Dict, Tuple
from rapidfuzz import fuzz
import logging

from app.domain.models import CompetenceDTO, Competence
from app.infrastructure.repositories.hybrid_competence_repository import HybridCompetenceRepository

logger = logging.getLogger(__name__)


class CompetenceService:
    """
    Zentrale Service-Klasse für Kompetenzen-Matching.
    Nutzt Fuzzy-Matching für robustes Parsing von PDF/DOCX-Artefakten.
    """
    
    def __init__(self, repository: HybridCompetenceRepository):
        self.repository = repository
        self.fuzzy_threshold = 75  # Minimale Ähnlichkeit für Matches (0-100)
        self.min_length = 3  # Minimale Länge für Matching
    
    def extract_competences_from_text(
        self, 
        text: str, 
        role_context: Optional[str] = None
    ) -> List[CompetenceDTO]:
        """
        OPTIMIERT: Extrahiert Kompetenzen aus Text mit 3-Phasen-Strategie:
        1. Tokenisierung und Bereinigung
        2. Fuzzy-Matching gegen ESCO-Labels
        3. Deduplizierung und Ranking
        
        Args:
            text: Input-Text (Anforderungen, Aufgaben)
            role_context: Erkannte Job-Rolle (z.B. "IT & Softwareentwicklung")
        
        Returns:
            Liste deduplizierter CompetenceDTO Objekte
        """
        if not text or len(text) < 10:
            return []
        
        # Phase 1: Tokenisierung
        tokens = self._tokenize_text(text)
        if not tokens:
            return []
        
        # Phase 2: Fuzzy-Matching gegen Repository-Labels
        matched_labels: Dict[str, Tuple[str, float]] = {}  # canonical -> (matched_term, confidence)
        
        for token in tokens:
            best_match = self._find_best_match(token)
            if best_match:
                canonical_label, confidence = best_match
                # Speichere nur den höchsten Confidence-Score pro Label
                if canonical_label not in matched_labels or confidence > matched_labels[canonical_label][1]:
                    matched_labels[canonical_label] = (token, confidence)
        
        # Phase 3: Konvertierung zu DTOs mit Deduplizierung
        results: List[CompetenceDTO] = []
        seen_uris: Set[str] = set()
        
        for canonical_label, (source_term, confidence) in matched_labels.items():
            try:
                # Hole ESCO-Daten
                esco_uri, esco_id, group = self.repository.get_esco_uri_and_id(canonical_label)
                
                # Prüfe auf Duplikate
                if esco_uri and esco_uri in seen_uris:
                    continue
                seen_uris.add(esco_uri or canonical_label)
                
                # Erstelle DTO
                dto = CompetenceDTO(
                    original_term=source_term,
                    esco_label=canonical_label,
                    esco_uri=esco_uri or f"custom/{canonical_label.lower().replace(' ', '_')}",
                    esco_group_code=group,
                    confidence_score=confidence / 100.0,  # Normalisiere auf [0.0 - 1.0]
                    level=self.repository.get_level(canonical_label),
                    is_digital=self.repository.is_digital_skill(canonical_label),
                    source_domain="JobPosting",
                    role_context=role_context
                )
                results.append(dto)
                
            except Exception as e:
                logger.warning(f"Fehler bei der Verarbeitung von '{canonical_label}': {e}")
                continue
        
        logger.info(f"Extrahiert {len(results)} Kompetenzen aus Text (Rolle: {role_context})")
        return results
    
    def _tokenize_text(self, text: str) -> List[str]:
        """
        Tokenisiert Text in Kandidaten-Terms.
        - Entfernt Stop-Words
        - Gruppiert Phrasen (2-3 Wörter)
        - Normalisiert Case
        """
        import re
        
        # Normalisiere
        text = text.lower().strip()
        
        # Entferne Sonderzeichen, behalte Leerzeichen und Bindestriche
        text = re.sub(r'[^\w\s\-]', '', text)
        
        # Teile in Worte
        words = text.split()
        
        # Filtere Stop-Words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'as', 'is', 'are', 'was',
            'der', 'die', 'das', 'und', 'oder', 'aber', 'in', 'auf', 'zu', 'mit',
            'von', 'durch', 'aus', 'über', 'am', 'im', 'ein', 'eine', 'einen'
        }
        
        filtered_words = [w for w in words if w not in stop_words and len(w) >= self.min_length]
        
        # Generiere n-grams (einzelne Worte und 2-Wort-Phrasen)
        tokens: List[str] = []
        
        # Einzelne Worte
        tokens.extend(filtered_words)
        
        # 2-Wort-Phrasen
        for i in range(len(filtered_words) - 1):
            bigram = f"{filtered_words[i]} {filtered_words[i+1]}"
            if len(bigram) >= self.min_length:
                tokens.append(bigram)
        
        # 3-Wort-Phrasen (optional, nur lange)
        for i in range(len(filtered_words) - 2):
            trigram = f"{filtered_words[i]} {filtered_words[i+1]} {filtered_words[i+2]}"
            if len(trigram) >= 15:  # Nur längere Phrasen
                tokens.append(trigram)
        
        # Dedupliziere und sortiere nach Länge (längere zuerst = höhere Priorität)
        unique_tokens = list(dict.fromkeys(tokens))  # Deduplizierung mit Order erhalt
        unique_tokens.sort(key=len, reverse=True)
        
        return unique_tokens[:500]  # Limit zur Performance
    
    def _find_best_match(self, token: str) -> Optional[Tuple[str, float]]:
        """
        Findet den besten ESCO-Label-Match für einen Token mittels Fuzzy-Matching.
        
        Returns:
            Tuple (canonical_label, confidence_score) oder None
        """
        if not token or len(token) < self.min_length:
            return None
        
        # Hole alle ESCO-Labels
        all_labels = self.repository.get_all_identifiable_labels()
        if not all_labels:
            return None
        
        best_score = 0
        best_label = None
        
        # Fuzzy-Match gegen alle Labels
        for label in all_labels:
            # Verwende token_sort_ratio für bessere Phrase-Matching
            score = fuzz.token_sort_ratio(token.lower(), label.lower())
            
            if score > best_score and score >= self.fuzzy_threshold:
                best_score = score
                best_label = label
        
        return (best_label, best_score) if best_label else None
    
    def filter_blacklist(self, competences: List[CompetenceDTO]) -> List[CompetenceDTO]:
        """
        Filtert Kompetenzen gegen die Domain-Blacklist.
        """
        blacklist = self.repository.get_blacklist()
        if not blacklist:
            return competences
        
        filtered = [
            c for c in competences 
            if c.original_term.lower() not in blacklist
            and c.esco_label and c.esco_label.lower() not in blacklist
        ]
        
        logger.info(f"Blacklist gefiltert: {len(competences)} -> {len(filtered)}")
        return filtered
    
    def apply_role_context_weighting(
        self, 
        competences: List[CompetenceDTO],
        role: Optional[str] = None
    ) -> List[CompetenceDTO]:
        """
        OPTIONAL: Gewichtet Kompetenzen basierend auf Rollenkontext.
        Erhöht Confidence für rollen-relevante Skills.
        """
        if not role:
            return competences
        
        role_keywords = self._get_role_keywords(role)
        
        weighted = []
        for comp in competences:
            # Prüfe ob Kompetenz zur Rolle passt
            matches_role = any(
                keyword.lower() in (comp.esco_label or "").lower()
                for keyword in role_keywords
            )
            
            if matches_role:
                # Erhöhe Confidence leicht (max 1.0)
                comp.confidence_score = min(1.0, comp.confidence_score * 1.1)
            
            comp.role_context = role
            weighted.append(comp)
        
        return weighted
    
    def _get_role_keywords(self, role: str) -> List[str]:
        """Extrahiert Keywords basierend auf Rolle"""
        role_maps = {
            "IT & Softwareentwicklung": ["python", "java", "database", "api", "develop", "code", "git"],
            "UX/UI Design": ["design", "ux", "ui", "figma", "prototype", "user", "interface"],
            "Management & Beratung": ["manage", "lead", "strategy", "consult", "plan"],
            "Finanzen & Controlling": ["finance", "accounting", "budget", "audit", "control"],
            "Assistenz & Office": ["admin", "office", "support", "organize"],
        }
        
        return role_maps.get(role, [])


class AnalysisOrchestrator:
    """
    Orchestriert die gesamte Analyse-Pipeline.
    Koordiniert Metadata-Extraktion, Kompetenzen-Matching und Speicherung.
    """
    
    def __init__(
        self, 
        competence_service: CompetenceService,
        repository: HybridCompetenceRepository
    ):
        self.competence_service = competence_service
        self.repository = repository
        self.logger = logging.getLogger(__name__)
    
    def analyze_job_posting(
        self,
        raw_text: str,
        title: str,
        job_role: str,
        tasks_section: str = "",
        requirements_section: str = ""
    ) -> List[CompetenceDTO]:
        """
        Führt eine komplette Analyse-Pipeline durch.
        
        Args:
            raw_text: Vollständiger Job-Text
            title: Job-Titel
            job_role: Erkannte Job-Rolle
            tasks_section: Extrahierte Aufgaben (optional)
            requirements_section: Extrahierte Anforderungen (optional)
        
        Returns:
            Liste analysierten Kompetenzen
        """
        # Wähle den Text für Analyse (segmentiert oder vollständig)
        analysis_text = (tasks_section + " " + requirements_section).strip()
        if not analysis_text or len(analysis_text) < 50:
            analysis_text = raw_text
        
        self.logger.info(f"Analysiere Job: {title} ({job_role})")
        
        # Phase 1: Kompetenzen-Extraktion
        competences = self.competence_service.extract_competences_from_text(
            analysis_text,
            role_context=job_role
        )
        
        # Phase 2: Blacklist-Filter
        competences = self.competence_service.filter_blacklist(competences)
        
        # Phase 3: Rollenkontext-Gewichtung
        competences = self.competence_service.apply_role_context_weighting(competences, job_role)
        
        # Phase 4: Sorting nach Confidence
        competences.sort(key=lambda c: c.confidence_score, reverse=True)
        
        self.logger.info(f"Analyse abgeschlossen: {len(competences)} Kompetenzen erkannt")
        
        return competences
