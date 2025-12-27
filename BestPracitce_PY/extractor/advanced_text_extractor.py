# infrastructure/extractor/advanced_text_extractor.py

from core.text_extraction_interface import TextExtractorInterface
from typing import Optional
import os
import PyPDF2 # Wird für PDF-Dateien benötigt
from docx import Document # Wird für DOCX-Dateien benötigt
# import fitz wurde entfernt, da es den Fehler verursacht.

class AdvancedTextExtractor(TextExtractorInterface):
    """
    Erweiterte Implementierung des TextExtractorInterface,
    die PDF, DOCX und einfache TXT-Dateien verarbeiten kann.
    """

    def extract_text(self, file_path: str) -> Optional[str]:
        extension = os.path.splitext(file_path)[1].lower()

        if extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif extension == '.docx':
            return self._extract_from_docx(file_path)
        elif extension == '.txt':
            # Wiederverwendung der TXT-Logik
            return self._extract_from_txt(file_path)
        else:
            print(f"[Extractor] Fehler: Dateiformat '{extension}' wird nicht unterstützt.")
            return None

    def _extract_from_txt(self, file_path: str) -> Optional[str]:
        # Implementierung wie im SimpleTextExtractor
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None

    def _extract_from_docx(self, file_path: str) -> Optional[str]:
        """Extrahiert Text aus DOCX mit python-docx."""
        try:
            document = Document(file_path)
            paragraphs = [p.text for p in document.paragraphs]
            return '\n'.join(paragraphs)
        except Exception as e:
            print(f"[Extractor] Fehler beim DOCX-Lesen: {e}")
            return None

    def _extract_from_pdf(self, file_path: str) -> Optional[str]:
        """Extrahiert Text aus PDF mit PyPDF2."""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"[Extractor] Fehler beim PDF-Lesen: {e}")
            return None
