# normalize.py

import re
from datetime import datetime, timedelta
from typing import Tuple, Optional, List

# --------------------------------------------------------------------
# A. DATUMS-NORMALISIERUNG
# --------------------------------------------------------------------

def parse_date(text: str, now_utc: Optional[datetime] = None) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extrahiert Veröffentlichungsdatum aus Rohtext mit umfassenden Pattern-Matching.

    Unterstützt:
    - Relative Datumsangaben: "vor 4 Tagen", "vor 2 Wochen"
    - ISO-Format: 2024-10-27
    - Deutsches Format: 27.10.2024, 27. Oktober 2024
    - Monat Jahr: Oktober 2024, Oct 2024
    - Stand/Copyright: Stand: 2024, © 2024
    - Heute/Gestern

    Returns:
        Tuple[ISO_Datum (YYYY-MM-DD), Gefundener_Term, Jahr]
    """
    if now_utc is None:
        now_utc = datetime.now()

    current_year = now_utc.year
    normalized_text = text.lower()

    # ========================================
    # PRIORITY 1: ISO-Datum (2024-10-27)
    # ========================================
    iso_match = re.search(r'(20[12]\d)-(\d{2})-(\d{2})', text[:2000])
    if iso_match:
        year = int(iso_match.group(1))
        if 2018 <= year <= current_year:
            iso_date = iso_match.group(0)
            return iso_date, iso_match.group(0), str(year)

    # ========================================
    # PRIORITY 2: Deutsches Datum (27.10.2024)
    # ========================================
    de_date_match = re.search(r'(\d{1,2})\.(\d{1,2})\.(20[12]\d)', text[:2000])
    if de_date_match:
        day = int(de_date_match.group(1))
        month = int(de_date_match.group(2))
        year = int(de_date_match.group(3))
        if 2018 <= year <= current_year and 1 <= month <= 12 and 1 <= day <= 31:
            try:
                iso_date = f"{year:04d}-{month:02d}-{day:02d}"
                return iso_date, de_date_match.group(0), str(year)
            except:
                pass

    # ========================================
    # PRIORITY 3: Monat Jahr (Oktober 2024, Oct 2024)
    # ========================================
    month_names_de = {
        'januar': 1, 'februar': 2, 'märz': 3, 'april': 4, 'mai': 5, 'juni': 6,
        'juli': 7, 'august': 8, 'september': 9, 'oktober': 10, 'november': 11, 'dezember': 12,
        'jan': 1, 'feb': 2, 'mär': 3, 'apr': 4, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'okt': 10, 'nov': 11, 'dez': 12,
        'march': 3, 'may': 5, 'oct': 10, 'dec': 12  # EN fallback
    }

    month_pattern = r'(januar|februar|märz|april|mai|juni|juli|august|september|oktober|november|dezember|jan|feb|mär|apr|jun|jul|aug|sep|okt|nov|dez|march|may|oct|dec)[^\d]*(20[12]\d)'
    month_match = re.search(month_pattern, normalized_text[:2000])
    if month_match:
        month_str = month_match.group(1)
        year = int(month_match.group(2))
        month = month_names_de.get(month_str, None)
        if month and 2018 <= year <= current_year:
            # Nutze Monatsmitte als Standardwert
            iso_date = f"{year:04d}-{month:02d}-15"
            return iso_date, month_match.group(0), str(year)

    # ========================================
    # PRIORITY 4: "Stand: 2024", "Copyright 2024", "© 2024"
    # ========================================
    stand_match = re.search(r'(?:stand|copyright|veröffentlicht|published|©)[^\d]*(20[12]\d)', normalized_text[:2000])
    if stand_match:
        year = int(stand_match.group(1))
        if 2018 <= year <= current_year:
            # Nutze Jahresmitte
            iso_date = f"{year:04d}-06-15"
            return iso_date, stand_match.group(0), str(year)

    # ========================================
    # PRIORITY 5: Einfach "2024" im Text (häufigstes Jahr)
    # ========================================
    years = re.findall(r'\b(20[12]\d)\b', text[:2000])
    if years:
        from collections import Counter
        year_counts = Counter(years)
        most_common_year = int(year_counts.most_common(1)[0][0])
        if 2018 <= most_common_year <= current_year:
            iso_date = f"{most_common_year:04d}-06-15"
            return iso_date, f"{most_common_year}", str(most_common_year)

    # ========================================
    # PRIORITY 6: Relative Datumsangaben
    # ========================================
    time_delta_match = re.search(
        r'vor\s+(\d+)\s*(tag|woche|monat|jahr)en?',
        normalized_text,
        re.IGNORECASE
    )
    if time_delta_match:
        value = int(time_delta_match.group(1))
        unit = time_delta_match.group(2)

        if unit.startswith('tag'):
            posting_date = now_utc - timedelta(days=value)
        elif unit.startswith('woche'):
            posting_date = now_utc - timedelta(weeks=value)
        elif unit.startswith('monat'):
            posting_date = now_utc - timedelta(days=30 * value)
        elif unit.startswith('jahr'):
            posting_date = now_utc - timedelta(days=365 * value)
        else:
            return None, None, None

        iso_date = posting_date.strftime("%Y-%m-%d")
        year = posting_date.strftime("%Y")
        return iso_date, time_delta_match.group(0), year

    # ========================================
    # PRIORITY 7: "Heute", "Gestern"
    # ========================================
    if 'heute' in normalized_text:
        iso_date = now_utc.strftime("%Y-%m-%d")
        return iso_date, 'heute', str(now_utc.year)

    if 'gestern' in normalized_text:
        yesterday = now_utc - timedelta(days=1)
        iso_date = yesterday.strftime("%Y-%m-%d")
        return iso_date, 'gestern', str(yesterday.year)

    # ========================================
    # FALLBACK: Aktuelles Jahr (PDFs meist aktuell)
    # ========================================
    iso_date = f"{current_year:04d}-06-15"
    return iso_date, "fallback", str(current_year)

# --------------------------------------------------------------------
# B. TEXT-BEREINIGUNG UND NORMALISIERUNG (Optionale Funktionen)
# --------------------------------------------------------------------

def clean_and_normalize_text(text: str) -> str:
    """
    Führt grundlegende Bereinigungs- und Normalisierungsschritte durch:
    - Kleinbuchstaben
    - Entfernt doppelte Leerzeichen und Zeilenumbrüche
    - Entfernt spezifische Steuerzeichen (z.B. \x00, was bereits im Workflow Manager geschieht)
    """

    # Text in Kleinbuchstaben umwandeln
    text = text.lower()

    # Entferne typische Steuerzeichen aus OCR/Parsing-Fehlern
    text = text.replace('\x00', '').replace('\u200b', '')

    # Entferne überflüssige Whitespace und Zeilenumbrüche (kann bei NLP hilfreich sein)
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def normalize_competence_term(term: str) -> str:
    """
    Normalisiert einen einzelnen Kompetenzbegriff (z.B. für das Caching oder Mapping).
    """
    return term.lower().strip()
