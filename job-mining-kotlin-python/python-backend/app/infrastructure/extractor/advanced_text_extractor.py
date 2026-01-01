import os
import tempfile
import logging
from typing import BinaryIO, Optional
from pypdf import PdfReader
from docx import Document

# Korrekter Import des Interfaces
from app.interfaces.interfaces import ITextExtractor

logger = logging.getLogger(__name__)

class AdvancedTextExtractor(ITextExtractor):
    """
    Liest rohe Bytes (PDF, DOCX, TXT) und wandelt sie in einen sauberen String um.
    Kennt keine Business-Logik, nur Dateiformate.
    """

    def extract_text(self, file_stream: BinaryIO, filename: str) -> str:
        """
        Hauptmethode: Entscheidet anhand der Dateiendung, welcher Parser genutzt wird.
        """
        # Sicherheitsnetz: Stream auf Anfang setzen
        file_stream.seek(0)

        # Dateiendung normalisieren (kleingeschrieben)
        file_ext = os.path.splitext(filename)[1].lower()

        try:
            if file_ext == '.pdf':
                return self._extract_from_pdf(file_stream, filename)
            elif file_ext == '.docx':
                return self._extract_from_docx(file_stream)
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                # ✅ BEST PRACTICE: Screenshot/Bild-Support via OCR
                # Speichere Stream temporär für Bild-OCR
                try:
                    with tempfile.NamedTemporaryFile(mode='wb', suffix=file_ext, delete=False) as tmp_file:
                        file_stream.seek(0)
                        tmp_file.write(file_stream.read())
                        tmp_path = tmp_file.name

                    # Bild-OCR
                    text = self._extract_from_image(tmp_path)

                    # Cleanup
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass

                    return text
                except Exception as img_e:
                    logger.error(f"Bild-Extraktion fehlgeschlagen für {filename}: {img_e}")
                    return ""
            elif file_ext in ['.txt', '.csv', '.rtf', '.md']:
                # Fallback: Text decodieren, Fehlerzeichen ignorieren
                return file_stream.read().decode('utf-8', errors='ignore')
            else:
                logger.warning(f"⚠️ Warnung: Unbekanntes Format '{file_ext}' bei {filename}. Versuche Text-Lesen.")
                return file_stream.read().decode('utf-8', errors='ignore')

        except Exception as e:
            logger.error(f"❌ Kritischer Fehler beim Lesen von {filename}: {e}")
            return ""

    def _extract_from_pdf(self, file_stream: BinaryIO, filename: str = "unknown.pdf") -> str:
        """
        ✅ BEST PRACTICE: Multi-Methode PDF-Extraktion mit OCR Fallback

        Extraction-Kette:
        1. pypdf (PdfReader) - Schnellste Methode
        2. pdfminer.six - Alternative bei Problemen
        3. OCR (pytesseract) - Fallback für gescannte PDFs

        Args:
            file_stream: PDF als BinaryIO
            filename: Dateiname für Logging

        Returns:
            Extrahierter Text
        """
        text_parts = []
        try:
            # METHODE 1: pypdf (Standard)
            reader = PdfReader(file_stream)
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text_parts.append(content)

            extracted_text = "\n".join(text_parts)

            # ✅ BEST PRACTICE: Fallback bei zu kurzem Text (< 100 Zeichen)
            if len(extracted_text.strip()) < 100:
                logger.warning(f"⚠️ PDF-Text zu kurz ({len(extracted_text)} Zeichen) für {filename}")

                # METHODE 2: pdfminer.six Fallback
                try:
                    from pdfminer.high_level import extract_text as pdfminer_extract_text
                    file_stream.seek(0)
                    alt_text = pdfminer_extract_text(file_stream)
                    if alt_text and len(alt_text.strip()) > len(extracted_text.strip()):
                        logger.info(f"✅ pdfminer-Fallback erfolgreich: {len(alt_text)} Zeichen")
                        extracted_text = alt_text
                except Exception as e:
                    logger.debug(f"pdfminer Fallback fehlgeschlagen: {e}")

                # METHODE 3: OCR Fallback (für gescannte PDFs)
                if len(extracted_text.strip()) < 100:
                    logger.warning(f"⚠️ Text immer noch zu kurz, versuche OCR Fallback")

                    # Speichere Stream temporär für OCR
                    try:
                        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as tmp_file:
                            file_stream.seek(0)
                            tmp_file.write(file_stream.read())
                            tmp_path = tmp_file.name

                        # OCR Extraktion
                        ocr_text = self._perform_ocr_fallback(tmp_path)

                        # Cleanup
                        try:
                            os.unlink(tmp_path)
                        except:
                            pass

                        if ocr_text and len(ocr_text.strip()) > len(extracted_text.strip()):
                            logger.info(f"✅ OCR-Fallback erfolgreich: {len(ocr_text)} Zeichen")
                            return ocr_text

                    except Exception as ocr_e:
                        logger.error(f"OCR-Fallback fehlgeschlagen: {ocr_e}")

            return extracted_text

        except Exception as e:
            logger.error(f"❌ PDF-Parsing Fehler für {filename}: {e}")
            return ""

    def _extract_from_docx(self, file_stream: BinaryIO) -> str:
        text_parts = []
        try:
            document = Document(file_stream)
            for para in document.paragraphs:
                if para.text:
                    text_parts.append(para.text)
            return "\n".join(text_parts)
        except Exception as e:
            print(f"❌ DOCX-Parsing Fehler: {e}")
            return ""

    def _perform_ocr_fallback(self, file_path: str) -> str:
        """
        ✅ BEST PRACTICE: OCR Fallback für gescannte PDFs und Screenshots

        Verwendet pdf2image + pytesseract für Text-Extraktion aus Bildern.
        Wichtig für:
        - Gescannte PDFs (ohne Text-Layer)
        - Screenshots von Job-Portalen
        - Alte PDF-Archive

        Args:
            file_path: Pfad zur Datei (PDF oder Bild)

        Returns:
            Extrahierter Text via OCR oder leerer String bei Fehler
        """
        try:
            from pdf2image import convert_from_path
            import pytesseract
        except ImportError as e:
            logger.warning(f"OCR-Bibliotheken nicht verfügbar: {e}")
            logger.warning("Install: pip install pdf2image pytesseract")
            logger.warning("System: apt-get install tesseract-ocr tesseract-ocr-deu poppler-utils")
            return ""

        try:
            logger.info(f"🔍 OCR Fallback für: {file_path}")

            # Konvertiere PDF/Bild zu Bildern
            images = convert_from_path(file_path, dpi=200)

            text_parts = []
            for i, image in enumerate(images[:20], 1):  # Max 20 Seiten für Performance
                try:
                    # Tesseract mit deutschem Sprachpaket
                    page_text = pytesseract.image_to_string(image, lang='deu')
                    if page_text.strip():
                        text_parts.append(page_text)
                    logger.debug(f"   OCR Seite {i}: {len(page_text)} Zeichen")
                except Exception as e:
                    logger.warning(f"   OCR Seite {i} fehlgeschlagen: {e}")
                    continue

            full_text = "\n".join(text_parts)
            logger.info(f"✅ OCR erfolgreich: {len(full_text)} Zeichen aus {len(images)} Seite(n)")
            return full_text

        except Exception as e:
            logger.error(f"❌ OCR Fallback fehlgeschlagen: {e}")
            return ""

    def _extract_from_image(self, file_path: str) -> str:
        """
        ✅ BEST PRACTICE: Direkte OCR-Extraktion für Bild-Dateien

        Für Screenshots und Bilder von Job-Anzeigen.

        Args:
            file_path: Pfad zum Bild (.jpg, .jpeg, .png)

        Returns:
            Extrahierter Text via OCR
        """
        try:
            import pytesseract
            from PIL import Image
        except ImportError as e:
            logger.warning(f"OCR-Bibliotheken nicht verfügbar: {e}")
            return ""

        try:
            logger.info(f"🖼️ Bild-OCR für: {file_path}")

            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang='deu')

            logger.info(f"✅ Bild-OCR erfolgreich: {len(text)} Zeichen")
            return text

        except Exception as e:
            logger.error(f"❌ Bild-OCR fehlgeschlagen: {e}")
            return ""
