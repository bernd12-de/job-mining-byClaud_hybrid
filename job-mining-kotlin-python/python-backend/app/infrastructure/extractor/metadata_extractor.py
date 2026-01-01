import re
import os
from typing import Dict, Optional

# Import für Zeitreihen-Analyse (Ebene 7)
try:
    from app.core.normalize import parse_date
except ImportError:
    def parse_date(text): return ("2024-01-01", None, None)

class MetadataExtractor:
    """
    Kombiniert deine detaillierten Kategorien mit den
    notwendigen Feldern für die Kotlin-Datenklassen.
    """

    def __init__(self):
        # URL-Pattern für Titel-Validierung (verhindert URLs als Titel)
        self.URL_PATTERN = re.compile(
            r'(?:https?://|www\.|[\w-]+\.(?:com|de|org|net|io|edu|gov|info|biz))',
            re.IGNORECASE
        )

        # OPTIMIERTE ROLLENERKENNUNG: Priorisiert nach Spezifität (Ebene 1: Erkennung)
        self.category_patterns = {
            # Level 1: Spezifische IT-Rollen (höchste Priorität)
            "IT & Softwareentwicklung": r"\b(softwareentwickler|software engineer|frontend|backend|fullstack|architect|devops|infra\s?engineer|entwickler|developer|programmier|python|java|kotlin|golang|rust|scala|c\+\+|typescript|node\.js|react|angular|vue\.js|sprint|agile|scrum master|release manager|quality assurance|qa engineer|qa|tester|automation|ci\/cd|jenkins|gitlab|github|docker|kubernetes|cloud|aws|azure|gcp|saas|platform|software|it[\s-]?security|cyber\s?security)\b",
            
            # Level 2: Design & UX (mittlere Priorität)
            "UX/UI Design": r"\b(ux[\s-]?design|ui[\s-]?design|user[\s-]?experience|user[\s-]?interface|ux[\s-]?engineer|ui[\s-]?engineer|ux[\s-]?researcher|designer|grafik|concept|visual|interaction|wireframe|prototyp|figma|sketch|adobe|photoshop)\b",
            
            # Level 3: Management & Beratung
            "Management & Beratung": r"\b(manager|management|consultant|consulting|berater|leitung|führungskraft|strategie|geschäftsführer|executive|director|head\s?of|product[\s-]?owner|product[\s-]?manager|account[\s-]?manager|project[\s-]?manager|stakeholder|business[\s-]?analyst|change[\s-]?management)\b",
            
            # Level 4: Finanzen & Controlling
            "Finanzen & Controlling": r"\b(finanz|financial|accounting|buchhaltung|controlling|bilanz|wirtschaftsprüf|buchhalter|ifrs|corporate finance|treasury|audit|financial analyst|cost accounting|tax)\b",
            
            # Level 5: Assistenz & Admin
            "Assistenz & Office": r"\b(assistenz|sekretariat|büro|office|administration|verwaltung|sachbearbeiter|office[\s-]?manager|executive[\s-]?assistant|admin|hr[\s-]?assistant|compliance|legal)\b",
        }
        # Optimierte Location-Patterns mit Wortwort-Grenzen
        self.location_patterns = r"\b(berlin|hamburg|münchen|köln|frankfurt|stuttgart|düsseldorf|gummersbach|mainz|augsburg|leipzig|dortmund|essen|bremen|hannover|nürnberg|mannheim|karlsruhe|bochum)\b"
        # Cache für kompilierte Patterns
        self._compiled_patterns = {k: re.compile(v, re.IGNORECASE) for k, v in self.category_patterns.items()}

        # Abschnitte, die für Kompetenzen irrelevante Inhalte enthalten (Benefits, About us, Kontakt)
        self.EXCLUDE_SECTIONS = re.compile(
            r"(wir bieten|benefits|was wir bieten|what we offer|about us|über uns|ueber uns|why us|warum wir|unternehmen|kontakt|bewerbung)",
            re.IGNORECASE,
        )

        # DEINE SEKTIONS-MUSTER (Lookahead-Version für bessere Segmentierung)
        self.TASK_PATTERN = re.compile(
            r'(?:DEINE AUFGABEN|TÄTIGKEITEN|WAS DU BEI UNS MACHST|YOUR TASKS|RESPONSIBILITIES|TASKS|WHAT YOU WILL DO)[\s\r\n:.-]+(.*?)(?=(?:DEIN PROFIL|PROFIL|REQUIREMENTS|WIR BIETEN|WIR SUCHEN|BENEFITS|ABOUT US|$))',
            re.DOTALL | re.IGNORECASE)

        self.REQ_PATTERN = re.compile(
            r'(?:PROFIL|DEIN PROFIL|YOUR PROFILE|ANFORDERUNGEN|REQUIREMENTS|QUALIFICATIONS|VORAUSSETZUNGEN|SKILLSET)[\s\r\n:.-]+(.*?)(?=(?:DEINE AUFGABEN|TASKS|WIR BIETEN|WIR SUCHEN|BENEFITS|KONTAKT|$))',
            re.DOTALL | re.IGNORECASE)

    def extract_all(self, text: str, filename: str, filepath: str = "") -> Dict:
        """
        Gibt das Dictionary zurück, das exakt zum AnalysisResultDTO passt.
        """
        iso_date, _, _ = parse_date(text)
        filtered_text = self._strip_irrelevant_sections(text)

        tasks_match = self.TASK_PATTERN.search(filtered_text)
        reqs_match = self.REQ_PATTERN.search(filtered_text)

        tasks_clean = tasks_match.group(1).strip() if tasks_match else ""
        reqs_clean = reqs_match.group(1).strip() if reqs_match else ""

        # Segmentierung validieren (Ebene 6)
        clean_segment = f"{tasks_clean} {reqs_clean}".strip()
        is_segmented = bool(tasks_clean or reqs_clean) and len(clean_segment) > 50

        # WICHTIG: Felder für die wissenschaftliche Validierung (Ebene 4/5)
        inferred_level = 2
        source_domain = "Stellenanzeige"
        if "fachbuecher" in filepath.lower():
            inferred_level = 4
            source_domain = f"Fachbuch: {filename}"
        elif "modulhandbuecher" in filepath.lower():
            inferred_level = 5
            source_domain = f"Academia: {filename}"

        # RETURN: Mappt exakt auf die Variablen in Kotlin
        return {
            "job_title": self._extract_title(text, filename),
            "job_role": self._extract_job_category(text), # Mappt auf AnalysisResultDTO.jobRole
            "region": self._extract_location(text),       # Mappt auf AnalysisResultDTO.region
            "industry": self._extract_organization(text), # Hier als Branche/Firma genutzt
            "posting_date": iso_date or "2024-01-01",
            "is_segmented": is_segmented,
            "processing_text": clean_segment if is_segmented else filtered_text,
            "inferred_level": inferred_level,
            "source_domain": source_domain,
            "tasks_clean": tasks_clean,
            "requirements_clean": reqs_clean,
            "raw_text": text
        }

    def _extract_title(self, text: str, filename: str) -> str:
        """
        Extrahiert den Jobtitel aus den ersten Zeilen oder nutzt den Dateinamen.

        VERBESSERUNGEN:
        - Prüft erste 10 Zeilen (nicht nur erste)
        - Filtert URLs heraus (verhindert URL als Titel)
        - Robustere Titel-Erkennung
        """
        lines = text.split('\n')

        # Suche in den ersten 10 Zeilen
        for line in lines[:10]:
            if not line.strip():
                continue

            # Entferne Gender-Marker und Trennzeichen
            title = re.sub(r'\(m/w/d\)|\[all genders\]|\(gn\)|\|\s?.*', '', line, flags=re.IGNORECASE).strip()

            # WICHTIG: Skip URLs (verhindert "https://jobs.firma.de" als Titel)
            if self.URL_PATTERN.search(title):
                continue

            # Valider Titel gefunden
            if len(title) > 5:
                return title

        # Fallback: Dateiname (aber nur wenn er keine URL ist)
        if self.URL_PATTERN.search(filename):
            return "Stellenanzeige (Titel nicht erkannt)"

        return filename

    def _extract_organization(self, text: str) -> str:
        match = re.search(r'([A-Z][a-zäöüß]+\s(AG|GmbH|Group|KG|Deutschland))', text[:1000])
        return match.group(0) if match else "Unbekannte Firma"

    def _extract_location(self, text: str) -> str:
        """
        OPTIMIERTE LOCATIONS-ERKENNUNG:
        1. Erkennung: Remote-Arbeit
        2. Gruppierung: Städte und Regionen
        3. Aufbereitung: Normalisierung und Deduplizierung
        """
        # Phase 1: Remote-Detection
        if re.search(r"\b(remote|homeoffice|home\s?office|flexibel arbeiten|work[\s-]?from[\s-]?home)\b", text, re.IGNORECASE):
            return "Remote"

        # Phase 2: Stadt-Erkennung mit Wortwort-Grenzen
        matches = re.findall(self.location_patterns, text, re.IGNORECASE)
        if matches:
            # Phase 3: Normalisierung - zähle Häufigkeiten und gib häufigste zurück
            match_counts = {}
            for match in matches:
                normalized = match.strip().title()
                match_counts[normalized] = match_counts.get(normalized, 0) + 1
            return max(match_counts, key=match_counts.get)
        
        # Fallback: Bundesländer-Erkennung
        if re.search(r"\b(bayern|nrw|baden-württemberg|sachsen|hessen|nordrhein|schleswig)\b", text, re.IGNORECASE):
            return "Deutschland"
        
        return "Deutschland"

    def _extract_job_category(self, text: str) -> str:
        """
        OPTIMIERTE ROLLENERKENNUNG (3-Phase-Strategie):
        1. Erkennung: Sucht nach Job-Rollen-Keywords mit Wortwort-Grenzen
        2. Gruppierung: Priorisiert spezifische Matches nach Kategorien
        3. Aufbereitung: Normalisiert das Ergebnis
        """
        # Phase 1 & 2: Erkennung + Gruppierung durch prioritäten-geordnete Suche
        for category, pattern in self._compiled_patterns.items():
            if pattern.search(text):
                # Phase 3: Aufbereitung - Return normalisierte Kategorie
                return category
        
        # Fallback wenn keine Kategorie erkannt
        return "Sonstige Fachgebiete"

    def _strip_irrelevant_sections(self, text: str) -> str:
        """Entfernt Benefits/About/Kontakt-Abschnitte, damit Analyse nur fachliche Teile nutzt."""
        lines = text.splitlines()
        kept_lines = []
        skip_block = False

        heading_reset = re.compile(r"(aufgaben|tasks|tätigkeiten|profil|requirements|qualifikation)", re.IGNORECASE)

        for line in lines:
            if self.EXCLUDE_SECTIONS.search(line):
                skip_block = True
                continue

            # Neue relevante Überschrift beendet das Skipping
            if skip_block and heading_reset.search(line):
                skip_block = False

            if not skip_block:
                kept_lines.append(line)

        cleaned = "\n".join(kept_lines).strip()

        # Falls wir nichts behalten konnten, nutze den Originaltext als Fallback
        return cleaned if cleaned else text
