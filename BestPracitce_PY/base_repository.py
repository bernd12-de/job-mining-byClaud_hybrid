"""
repositories/base_repository.py
Abstract Repository Pattern
"""

from abc import ABC, abstractmethod
from typing import List
from models.competence import Competence


class BaseRepository(ABC):
    """
    Abstract Repository Pattern
    
    Nach: Gharbi (Softwarearchitektur) - Trennung von Verantwortlichkeiten
    """
    
    @abstractmethod
    def load(self) -> List[Competence]:
        """Lädt Kompetenzen aus Datenquelle"""
        pass
    
    @abstractmethod
    def is_enabled(self) -> bool:
        """Prüft ob Quelle aktiviert ist"""
        pass
    
    def save(self, competences: List[Competence]) -> bool:
        """
        Speichert Kompetenzen (optional)
        Standardmäßig read-only
        """
        raise NotImplementedError("Diese Quelle ist read-only")
