from abc import ABC, abstractmethod
from typing import List, Dict

class ICompetenceRepository(ABC):
    @abstractmethod
    def get_all_skills(self) -> List[str]:
        """Liefert die 31.655 ESCO-Labels (Ebene 2)"""
        pass

    @abstractmethod
    def get_all_esco_labels(self) -> List[str]:
        """Liefert die 31.655 bevorzugten Labels aus ESCO (Ebene 2)"""
        pass

    @abstractmethod
    def get_fachbuch_labels(self) -> List[str]:
        """Liefert Begriffe aus Architektur-PDFs (Ebene 4)"""
        pass

    @abstractmethod
    def get_academia_labels(self) -> List[str]:
        """Liefert Begriffe aus Modulhandbüchern (Ebene 5)"""
        pass

    @abstractmethod
    def is_digital_skill(self, term: str) -> bool:
        """Prüft den Digital-Hebel (Ebene 3)"""
        pass
