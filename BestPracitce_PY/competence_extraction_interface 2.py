# core/competence_extraction_interface.py

from abc import ABC, abstractmethod
from typing import List
from core.entities.job_posting import Competence

class CompetenceExtractorInterface(ABC):
    """
    Interface für Dienste, die Kompetenzen (Skills, Wissen, etc.)
    aus Rohtext extrahieren und als Competence-Entitäten zurückgeben.
    """

    @abstractmethod
    def extract_competences(self, raw_text: str) -> List[Competence]:
        """
        Analysiert den Rohtext und gibt eine Liste von Competence-Objekten zurück.
        """
        pass
