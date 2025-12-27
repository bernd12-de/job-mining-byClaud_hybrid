from __future__ import annotations
import re
from datetime import datetime, date
from typing import Optional

_SPACY_AVAILABLE = False
_NLP = None

def _init_spacy():
    global _SPACY_AVAILABLE, _NLP
    if _NLP is not None:
        return
    try:
        import spacy
        for model in ["de_core_news_md", "de_core_news_sm", "en_core_web_sm"]:
            try:
                _NLP = spacy.load(model)
                _SPACY_AVAILABLE = True
                break
            except Exception:
                continue
    except Exception:
        _SPACY_AVAILABLE = False
        _NLP = None

def _clean(v: str) -> str:
    v = re.sub(r"[\u200B\u200C\u200D]+", "", v or "")
    v = re.sub(r"\s+", " ", v).strip(" :|\t\r\n-–—")
    return v

_COMPANY_SUFFIX = r"(?:AG|GmbH|SE|KG|OHG|e\.V\.|UG|Inc\.?|Ltd\.?|PLC|LLC|S\.A\.|S\.p\.A\.)"

_COMPANY_HINTS = [
    r"(?:Unternehmen|Firma|Arbeitgeber|Gesellschaft)\s*[:\-–]\s*(?P<val>.+?)(?:\s{2,}|\n|$)",
    r"(?:Company|Employer|Organization)\s*[:\-–]\s*(?P<val>.+?)(?:\s{2,}|\n|$)",
    r"(?:by|at)\s+(?P<val>[A-Z][\w&\-\., ]{2,}?(?:\sAG|\sGmbH|\sSE|\sKG|\sGmbH & Co\.\s*KG| Inc\.?| Ltd\.?)?)\b",
    r"(?P<val>[A-Z][\w&\-\., ]{2,}?(?:\sAG|\sGmbH|\sSE|\sKG|\sGmbH & Co\.\s*KG| Inc\.?| Ltd\.?))\s+(?:sucht|stellt.*ein|hiring|recruits)",
]

def _company_via_regex(text: str) -> Optional[str]:
    if not text: return None
    for m in re.finditer(rf"\b([A-ZÄÖÜ][\w&\-\., ]{{2,}}?\s{_COMPANY_SUFFIX})\b", text):
        cand = _clean(m.group(1))
        if 3 <= len(cand) <= 120: return cand
    for pat in _COMPANY_HINTS:
        m = re.search(pat, text, flags=re.IGNORECASE | re.MULTILINE)
        if m and m.group('val'):
            cand = _clean(m.group('val'))
            cand = re.split(r"(?:\s{2,}|\s\|\s|·|•|\||—|–|, for|, mit|, am)", cand)[0]
            if not re.search(r"\b(UX|UI|Senior|Junior|Werkstudent|Consultant|Engineer|Manager|Designer|Specialist)\b", cand, re.IGNORECASE):
                if 3 <= len(cand) <= 120: return cand
    return None

def _company_via_spacy(text: str) -> Optional[str]:
    _init_spacy()
    if not _SPACY_AVAILABLE or not text: return None
    try:
        doc = _NLP(text[:10000])
        orgs = [ent.text for ent in doc.ents if ent.label_.lower() in ('org','organization','unternehmen')]
        for t in orgs:
            t2 = _clean(t)
            if re.search(rf"\b{_COMPANY_SUFFIX}\b", t2):
                return t2
        return _clean(orgs[0]) if orgs else None
    except Exception:
        return None

def extract_company_name(text: str) -> Optional[str]:
    return _company_via_regex(text) or _company_via_spacy(text)

_LOCATION_HINTS = [
    r"(?:Standort|Ort|Einsatzort|Location)\s*[:\-–]\s*(?P<val>.+?)(?:\s{2,}|\n|$)",
    r"(?:Arbeitsort|Dienstort)\s*[:\-–]\s*(?P<val>.+?)(?:\s{2,}|\n|$)",
    r"\b(?:in|at)\s+(?P<val>[A-ZÄÖÜ][\w\-\.' ]+?)(?:\s*\(|,|\sbei|\sfür|\smit|\sremote|\s/hybrid|\s–|\s—|\s-|\.)",
]

_CITY_FIXES = {
    "Muenchen": "München",
    "Muenster": "Münster",
    "Koeln": "Köln",
    "Duesseldorf": "Düsseldorf",
}

def _post_loc(v: str) -> str:
    v = _clean(v)
    v = re.split(r"\s*\(|,|\s/\s|/|–|—|-", v)[0]
    v = _CITY_FIXES.get(v, v)
    if not (2 <= len(v) <= 80): return ""
    return v

def _loc_via_regex(text: str) -> Optional[str]:
    if not text: return None
    for pat in _LOCATION_HINTS:
        m = re.search(pat, text, flags=re.IGNORECASE | re.MULTILINE)
        if m and m.group('val'):
            loc = _post_loc(m.group('val'))
            if loc: return loc
    cities = r"(Berlin|München|Hamburg|Köln|Frankfurt|Stuttgart|Düsseldorf|Leipzig|Dresden|Nürnberg|Bremen|Hannover|Essen|Dortmund|Bonn|Münster|Karlsruhe|Heidelberg|Aachen|Zürich|Basel|Wien)"
    m = re.search(rf"\b{cities}\b", text, flags=re.IGNORECASE)
    if m: return _post_loc(m.group(0))
    return None

def _loc_via_spacy(text: str) -> Optional[str]:
    _init_spacy()
    if not _SPACY_AVAILABLE or not text: return None
    try:
        doc = _NLP(text[:10000])
        locs = [ent.text for ent in doc.ents if ent.label_.lower() in ('gpe','loc','ort','location')]
        return _post_loc(locs[0]) if locs else None
    except Exception:
        return None

def extract_location(text: str) -> Optional[str]:
    return _loc_via_regex(text) or _loc_via_spacy(text)

_DATE_PATTERNS = [
    r"(?:Veröffentlicht|Ausschreibung|Posting|Datum)\s*[:\-–]\s*(?P<val>\d{1,2}\.\d{1,2}\.\d{2,4})",
    r"(?P<val>\d{1,2}\.\d{1,2}\.\d{2,4})",
    r"(?P<val>\d{4}-\d{2}-\d{2})",
]

def _parse_date(val: str):
    val = val.strip()
    for fmt in ("%d.%m.%Y","%d.%m.%y","%Y-%m-%d"):
        try:
            return datetime.strptime(val, fmt).date()
        except Exception:
            continue
    return None

def extract_posting_date(text: str):
    if not text: return None
    for pat in _DATE_PATTERNS:
        m = re.search(pat, text)
        if m and m.group('val'):
            d = _parse_date(m.group('val'))
            if d: return d
    return None

_BRANCH_MAP = [
    (r"\bBahn|Rail|DB\b", "Transport"),
    (r"\bBank|Finanz|Finance|Versicherung|Insurance\b", "Finance"),
    (r"\bHealth|Hospital|Krankenhaus|Clinic|Pharma\b", "Healthcare"),
    (r"\bAutomotive|OEM|BMW|VW|Mercedes|Porsche|Audi\b", "Automotive"),
    (r"\bIT|Software|Tech|Cloud|SaaS|Digital\b", "Technology"),
    (r"\bTelekom|Telecom|Telecommunications\b", "Telecommunications"),
    (r"\bHandelsblatt|Verlag|Publishing|Media\b", "Media"),
    (r"\bBau|Construction|PERI\b", "Construction"),
]

def extract_branch(company_name: str) -> str:
    if not company_name: return "Unknown"
    for pat, branch in _BRANCH_MAP:
        if re.search(pat, company_name, flags=re.IGNORECASE):
            return branch
    return "Unknown"
