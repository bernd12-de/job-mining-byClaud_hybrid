"""
services/competence_extraction.py
Kompetenzextraktions-Service (REFACTORED)

WICHTIG: Enthält NUR Business-Logik, KEINE Daten!
Daten kommen vom Repository!

Nach: 
- Separation of Concerns (Gharbi)
- Single Responsibility (SOLID)
- Dependency Injection
"""

import logging
from typing import List
from pathlib import Path

# Domain Models
from models.job_ad import JobAd

# Repository Layer (Data Access)
from repositories.competence_repository import CompetenceRepository

# Service Layer (Business Logic)
from services.competence_matcher import CompetenceMatcher


class CompetenceExtractionService:
    """
    Service für Kompetenzextraktion
    
    Verantwortlichkeiten:
    - Orchestriert Extraktion
    - Business-Logik
    - Logging & Statistiken
    
    NICHT verantwortlich für:
    - Daten laden (macht Repository!)
    - Matching-Logik (macht Matcher!)
    
    Nach: Single Responsibility Principle
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Dependency Injection: Repository
        config_path = getattr(config, 'competence_config', None)
        if not config_path:
            # Default config path
            config_path = "data/competences/config/data_sources.yaml"
        
        self.repository = CompetenceRepository(config_path=config_path)
        
        # Dependency Injection: Matcher
        matching_config = {}
        if hasattr(config, 'matching_config'):
            matching_config = config.matching_config
        
        self.matcher = CompetenceMatcher(
            use_word_boundaries=matching_config.get('use_word_boundaries', True),
            case_sensitive=matching_config.get('case_sensitive', False),
            minimum_confidence=matching_config.get('minimum_confidence', 0.7)
        )
        
        # Lade Kompetenzbibliothek (beim Start)
        self._load_library()
    
    def _load_library(self):
        """Lädt Kompetenzbibliothek vom Repository"""
        self.logger.info("📚 Lade Kompetenzbibliothek...")
        
        self.competence_library = self.repository.get_all_competences()
        
        # Statistiken
        stats = self.repository.get_statistics()
        
        self.logger.info(f"✅ Bibliothek geladen:")
        self.logger.info(f"   Total: {stats['total']} Kompetenzen")
        self.logger.info(f"   Domains: {len(stats['by_domain'])}")
        self.logger.info(f"   Kategorien: {len(stats['by_category'])}")
        self.logger.info(f"   Mit Alternativen: {stats['with_alternatives']}")
    
    def extract_all(self, job_ads: List[JobAd]) -> List[JobAd]:
        """
        Extrahiert Kompetenzen aus allen Job Ads
        
        Args:
            job_ads: Liste von JobAd-Objekten
        
        Returns:
            Job Ads mit extrahierten Kompetenzen
        """
        self.logger.info(f"🔍 Extrahiere Kompetenzen aus {len(job_ads)} Stellenanzeigen...")
        
        total_found = 0
        
        for i, job in enumerate(job_ads, 1):
            # Text verwenden (cleaned wenn vorhanden, sonst raw)
            text = job.cleaned_text if job.cleaned_text else job.raw_text
            
            # Kompetenzen finden (Matcher macht die Arbeit!)
            found_competences = self.matcher.find_matches(
                text=text,
                competence_library=self.competence_library
            )
            
            # Zu JobAd hinzufügen
            job.competences = found_competences
            total_found += len(found_competences)
            
            # Logging
            if i % 10 == 0 or i == len(job_ads):
                avg = total_found / i
                self.logger.info(f"   [{i}/{len(job_ads)}] Ø {avg:.1f} Kompetenzen/Anzeige")
        
        # Final Statistics
        avg_final = total_found / len(job_ads) if job_ads else 0
        self.logger.info(f"✅ Extraktion abgeschlossen:")
        self.logger.info(f"   Total gefunden: {total_found} Kompetenzen")
        self.logger.info(f"   Ø pro Anzeige: {avg_final:.1f}")
        
        return job_ads
    
    def extract_single(self, job_ad: JobAd) -> JobAd:
        """Extrahiert Kompetenzen aus einzelner Job Ad"""
        text = job_ad.cleaned_text if job_ad.cleaned_text else job_ad.raw_text
        
        job_ad.competences = self.matcher.find_matches(
            text=text,
            competence_library=self.competence_library
        )
        
        return job_ad
    
    def get_available_domains(self) -> List[str]:
        """Gibt verfügbare Domains zurück"""
        stats = self.repository.get_statistics()
        return list(stats['by_domain'].keys())
    
    def get_available_categories(self) -> List[str]:
        """Gibt verfügbare Kategorien zurück"""
        stats = self.repository.get_statistics()
        return list(stats['by_category'].keys())
    
    def reload_library(self):
        """
        Lädt Bibliothek neu
        
        Nützlich wenn:
        - Neue JSON-Dateien hinzugefügt wurden
        - Config geändert wurde
        """
        self.logger.info("🔄 Lade Bibliothek neu...")
        self.repository.clear_cache()
        self._load_library()
    
    def get_extraction_stats(self) -> dict:
        """Gibt Service-Statistiken zurück"""
        repo_stats = self.repository.get_statistics()
        
        return {
            'library_stats': repo_stats,
            'matcher_config': {
                'use_word_boundaries': self.matcher.use_word_boundaries,
                'case_sensitive': self.matcher.case_sensitive,
                'minimum_confidence': self.matcher.minimum_confidence
            }
        }


# Export
__all__ = ['CompetenceExtractionService']
