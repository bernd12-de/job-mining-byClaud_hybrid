# domain/services/organization_service.py (NEU DOMAIN SERVICE)

import json
import re
from pathlib import Path
from typing import Dict
from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient

class OrganizationService:
    """
    Domain Service für die Branchen-Klassifizierung.
    Nutzt das DB-gestützte Regelwerk über den KotlinRuleClient.
    """

    def __init__(self, rule_client: KotlinRuleClient):
        # Lädt die Mappings beim Start einmalig in den Speicher
        # 🚨 DER FIX: Du musst den übergebenen Client an 'self' binden!
        self.rule_client = rule_client

        # Heuristische Schlüsselwörter als Fallback, wenn keine Regeln greifen (Ebene 3/4)
        self.keyword_industries = [
            ("IT & Softwareentwicklung", r"software|it|cloud|saas|devops|cyber|ai|ml|data|digitalisierung"),
            ("Finanzen & Controlling", r"bank|finance|versicherung|insurtech|treasury|buchhaltung|controlling|kredit"),
            ("Gesundheit & Pharma", r"klinik|health|medizin|pharma|arztpraxis|pflege|medtech|biotech"),
            ("Bildung & Forschung", r"hochschule|universität|university|school|campus|lehre|forschung|edu"),
            ("Logistik & Mobilität", r"logistik|supply chain|transport|flotte|fleet|shipping|verkehr|bahn|bus"),
            ("Energie & Umwelt", r"energie|strom|wind|solar|erneuerbar|utility|umwelt|co2|gruen|grün"),
            ("Handel & E-Commerce", r"e-commerce|shop|retail|handel|filiale|store|marketplace|pos"),
            ("Industrie & Produktion", r"produktion|fertigung|anlage|maschinenbau|industrial|factory|werk"),
            ("Telekommunikation", r"telekom|telco|5g|netz|carrier|broadband|dsl|mobilfunk"),
            ("Öffentlicher Sektor", r"behörde|verwaltung|amt|stadt|kommune|ministerium|oeffentlich|öffentlich"),
        ]

        # Primäre Regeln aus Kotlin, Fallback aus lokaler JSON, dann heuristik
        try:
            primary_mappings = self.rule_client.fetch_industry_mappings()
        except Exception:
            primary_mappings = {}

        self.industry_mappings: Dict[str, str] = primary_mappings or self._load_fallback_industry_mappings()

        # Wenn IMMER NOCH leer → Hardcoded Defaults
        if not self.industry_mappings:
            self.industry_mappings = {
                'IT & Software': r'Software|Entwicklung|Cloud|IT|Data|Informatik',
                'Finanzen': r'Bank|Versicherung|Finance|Finanz'
            }

        # industry_keywords = gleiche Daten (kein extra Fetch nötig)
        self.industry_keywords = self.industry_mappings

        print(f"✅ {len(self.industry_mappings)} Branchen-Regeln geladen.")




    def detect_industry(self, text: str) -> str:
        # 1) Regelseitig (Kotlin) primär
        rule_based = self.classify_industry(text, default_industry=None)
        if isinstance(rule_based, str) and rule_based:
            return rule_based

        # 2) Heuristisches Scoring auf Schlüsselwörtern
        heuristic = self._heuristic_industry(text)
        if heuristic:
            return heuristic

        # 3) Legacy-Keywords
        backup = self.classify_industry_neu(text)
        return backup if backup else "Sonstiges"



    def classify_industry(self, job_text: str, default_industry: str = "Sonstiges") -> str:
        """
        Klassifiziert die Branche anhand des gesamten Stellentextes mithilfe des Regelwerks.
        """
        text_lower = job_text.lower()
        scores = {}

        for industry, pattern in self.industry_mappings.items():
            try:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return industry
            except re.error:
                print(f"⚠️ Warnung: Ungültiges Regex-Muster für Branche '{industry}': {pattern}")
                continue

        return default_industry

    def classify_industry_neu(self, text: str) -> str:
        """Prüft den Text gegen die geladenen Keywords."""
        text_lower = text.lower()
        scores = {}

        for industry, pattern in self.industry_keywords.items():
            # Pattern ist z.B. "Bank|Versicherung"
            # Wir machen daraus eine RegEx-Suche
            try:
                hits = len(re.findall(f"({pattern})", text_lower, re.IGNORECASE))
                if hits > 0:
                    scores[industry] = hits
            except:
                continue

        if not scores:
            return "Unbekannt"

        # Gewinner ist die Branche mit den meisten Treffern
        return max(scores, key=scores.get)

    def _load_mappings(self) -> Dict[str, str]:
        """Holt Mappings von Kotlin (via Client)."""
        try:
            # Erwartet: {'IT': 'Software|Computer', 'Finance': 'Bank|Versicherung'}
            mappings = self.rule_client.fetch_industry_mappings()
            if mappings:
                print(f"✅ {len(mappings)} Branchen-Regeln geladen.")
                return mappings
        except Exception as e:
            print(f"⚠️ Fehler bei Branchen-Mappings: {e}")

        # Fallback auf lokale JSON oder minimale Defaults
        fallback = self._load_fallback_industry_mappings()
        if fallback:
            return fallback

        return {
            'IT & Software': 'Software|Entwicklung|Cloud|IT|Data',
            'Finanzen': 'Bank|Versicherung|Finance'
        }

    def _load_fallback_industry_mappings(self) -> Dict[str, str]:
        """Lädt lokale Fallback-Regeln aus data/fallback_rules/industry_mappings.json."""
        try:
            base_dir = Path(__file__).resolve().parents[3]
            json_path = base_dir / "data" / "fallback_rules" / "industry_mappings.json"
            if json_path.exists():
                with json_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
        except Exception as e:
            print(f"⚠️ Konnte Fallback-Branchen nicht laden: {e}")
        return {}

    def _heuristic_industry(self, text: str) -> str:
        """Einfache Schlüsselwort-basierte Zuordnung als Fallback-Layer."""
        text_lower = text.lower()
        scores = {}

        for industry, pattern in self.keyword_industries:
            try:
                hits = len(re.findall(pattern, text_lower, re.IGNORECASE))
                if hits:
                    scores[industry] = hits
            except re.error:
                continue

        if not scores:
            return ""

        return max(scores, key=scores.get)


