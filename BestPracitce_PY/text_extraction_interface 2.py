# core/text_extraction_interface.py

from abc import ABC, abstractmethod
from typing import Optional

class TextExtractorInterface(ABC):
    """
    Interface für Dienste, die reinen Text aus verschiedenen
    Stellenanzeigen-Dateiformaten extrahieren.
    """

    @abstractmethod
    def extract_text(self, file_path: str) -> Optional[str]:
        """
        Muss implementiert werden, um den Text aus dem gegebenen
        Dateipfad zu extrahieren.

        :param file_path: Der Pfad zur Stellenanzeigen-Datei auf dem lokalen System.
        :return: Der vollständige, extrahierte Rohtext oder None bei Fehler.
        """
        pass
