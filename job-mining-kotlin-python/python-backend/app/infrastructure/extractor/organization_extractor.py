# organization_extractor.py

import re

# Vordefinierte Branchen-Muster
INDUSTRY_PATTERNS = {
    "Unternehmensberatung & Finanzen": r"(KPMG|EY|Deloitte|PwC|Finanz|Consulting|Beratung|Versicherung)",
    "Maschinenbau & Industrie": r"(Dräger|STRABAG|ABUS Kransysteme|Maschinen|Anlagenbau|Fertigung)",
    "IT & Telekommunikation": r"(Telefónica|T-Systems|IT|Tech|Digitalagentur|Softwareentwicklung)",
    "E-Learning & Bildung": r"(Lingoda|Studyflix|Institut|Syntax)",
    "Medizin & Pharmazie": r"(Ottobock|Pharma|Medizin)",
    "Öffentlicher Dienst & Verkehr": r"(Hamburger Hochbahn|Verkehr|Städtisch|Bahn)"
}



def extract_branch(organization_name: str) -> str:
    """
    Versucht, die Branche basierend auf dem extrahierten Organisationsnamen
    oder bekannten Schlüsselbegriffen zuzuordnen.
    """
    normalized_name = organization_name.lower()

    for industry, pattern in INDUSTRY_PATTERNS.items():
        if re.search(pattern, normalized_name, re.IGNORECASE):
            return industry

    return "Sonstige/Unbekannte Branche"
