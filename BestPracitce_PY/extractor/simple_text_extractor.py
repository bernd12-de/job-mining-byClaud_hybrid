# infrastructure/extractor/simple_text_extractor.py

from core.text_extraction_interface import TextExtractorInterface
from typing import Optional

class SimpleTextExtractor(TextExtractorInterface):
    """
    Erste Implementierung des TextExtractorInterface.
    Liest den Inhalt einer einfachen .txt-Datei.
    Wird später durch Parser für PDF/DOCX erweitert oder ersetzt.
    """

    def extract_text(self, file_path: str) -> Optional[str]:
        """
        Liest den Inhalt einer Datei aus dem angegebenen Pfad.
        """
        try:
            # Stellt sicher, dass die Datei existiert und lesbar ist
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"[Extractor] Erfolgreich {len(content)} Zeichen aus {file_path} gelesen.")
                return content
        except FileNotFoundError:
            # Fehlerhandling, wenn die Datei nicht existiert
            print(f"[Extractor] Fehler: Datei nicht gefunden unter Pfad: {file_path}")
            return None
        except Exception as e:
            # Generisches Fehlerhandling
            print(f"[Extractor] Fehler beim Lesen der Datei {file_path}: {e}")
            return None
