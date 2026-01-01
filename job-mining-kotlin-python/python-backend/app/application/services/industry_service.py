"""
IndustryService - Industrie-Klassifizierung mit 7-Ebenen-Modell
================================================================

Klassifiziert Industrien hierarchisch nach:
- Ebene 5: Academia (Wissenschaft/Forschung aus Modulhandbüchern)
- Ebene 4: Fachbücher (Spezialisierte Branchen aus Fachliteratur)
- Ebene 3: Digital Industries (IT/Tech-Branchen mit Digital-Flag)
- Ebene 2: NACE Standard (EU-Klassifikation)
- Ebene 1: Discovery (Neue unbekannte Branchen)

Priorität: Academia (5) > Fachbuch (4) > Digital (3) > NACE (2) > Discovery (1)

Basis:
- NACE Rev. 2 (Nomenclature of Economic Activities)
- ESCO Industry Taxonomy
- Fachbücher & Stellenanzeigen
- Modulhandbücher (Academic Research)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class IndustryService:
    """
    Domain Service für die Klassifizierung von Industrien/Branchen.
    Nutzt 7-Ebenen-Modell analog zu HybridCompetenceRepository.
    """

    def __init__(self):
        # Ebene 5: Academia Industries (Wissenschaft/Forschung)
        self._academia_industries: Dict[str, int] = self._load_academia_industries()

        # Ebene 4: Fachbuch Industries (Spezialisierte Branchen)
        self._fachbuch_industries: Dict[str, int] = self._load_fachbuch_industries()

        # Ebene 3: Digital Industries (IT/Tech)
        self._digital_industries: Dict[str, int] = self._load_digital_industries()

        # Ebene 2: NACE Standard
        self._nace_industries: Dict[str, str] = self._load_nace_industries()

        # Pattern-basierte Klassifizierung (wie RoleService)
        self._setup_industry_patterns()

        print(f"✅ IndustryService initialisiert:")
        print(f"   • Academia (L5): {len(self._academia_industries)} Branchen")
        print(f"   • Fachbuch (L4): {len(self._fachbuch_industries)} Branchen")
        print(f"   • Digital (L3): {len(self._digital_industries)} Branchen")
        print(f"   • NACE (L2): {len(self._nace_industries)} Codes")

    # ═══════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════════════════

    def classify_industry(
        self,
        job_text: str,
        job_title: str = "",
        company_name: str = "",
        default_industry: str = "Sonstige Branche"
    ) -> str:
        """
        Klassifiziert die Branche anhand von Job-Text, Titel und Firma.

        Returns:
            Industrie-Name (z.B. "Informationstechnologie" oder "Maschinenbau")
        """
        search_target = f"{job_title} {job_text} {company_name}".lower()

        # Pattern-basierte Klassifizierung
        industry = self._classify_with_patterns(search_target)
        if industry != "Sonstige Branche":
            return industry

        return default_industry

    def get_industry_level(self, industry_name: str) -> int:
        """
        Gibt das Level einer Branche zurück (1-5).

        Priorität: Academia (5) > Fachbuch (4) > Digital (3) > NACE (2) > Discovery (1)
        """
        normalized = industry_name.lower().strip()

        # Ebene 5: Academia
        if normalized in self._academia_industries:
            return 5

        # Ebene 4: Fachbuch
        if normalized in self._fachbuch_industries:
            return 4

        # Ebene 3: Digital
        if normalized in self._digital_industries:
            return 3

        # Ebene 2: NACE
        if normalized in self._nace_industries.values():
            return 2

        # Ebene 1: Discovery (Fallback)
        return 1

    def is_digital_industry(self, industry_name: str) -> bool:
        """Prüft, ob eine Branche digital ist (Level 3 relevant)."""
        normalized = industry_name.lower().strip()
        return normalized in self._digital_industries

    # ═══════════════════════════════════════════════════════════════════
    # PATTERN-BASED CLASSIFICATION (wie RoleService)
    # ═══════════════════════════════════════════════════════════════════

    def _setup_industry_patterns(self):
        """
        Setup NACE/ESCO-basierte Industrie-Patterns

        Struktur: {Industrie: [Pattern-Liste]}
        Basiert auf NACE Rev. 2 + ESCO + Fachbücher + Stellenanzeigen
        """
        self.INDUSTRY_PATTERNS = {
            # ═══════════════════════════════════════════════════════════════
            # EBENE 5: ACADEMIA (Wissenschaft/Forschung)
            # ═══════════════════════════════════════════════════════════════

            "Wissenschaft & Forschung": [
                r"\bforschung|research|wissenschaft\b",
                r"\bforschungseinrichtung|forschungsinstitut\b",
                r"\bacademic|academia|universität|hochschule\b",
                r"\bmax.planck|fraunhofer|helmholtz|leibniz\b",
            ],

            # ═══════════════════════════════════════════════════════════════
            # EBENE 4: FACHBUCH (Spezialisierte Branchen)
            # ═══════════════════════════════════════════════════════════════

            "Biotech & Life Sciences": [
                r"\bbiotech|biotechnologie|life\s+sciences\b",
                r"\bpharma|pharmazeutik|medizintechnik\b",
                r"\bbiologie|genetik|genom\b",
            ],

            "Luft- & Raumfahrt": [
                r"\bluftfahrt|aerospace|aviation\b",
                r"\braumfahrt|space|satellit\b",
                r"\bairbus|boeing|esa\b",
            ],

            "Erneuerbare Energien": [
                r"\berneuerbar|renewable\s+energy|nachhaltig\b",
                r"\bsolar|wind|wasserkraft|photovoltaik\b",
                r"\benergie|energy|elektromobilität\b",
            ],

            # ═══════════════════════════════════════════════════════════════
            # EBENE 3: DIGITAL INDUSTRIES (IT/Tech)
            # ═══════════════════════════════════════════════════════════════

            "Informationstechnologie": [
                r"\bit\b|information\s+technology|software\b",
                r"\btech|technology|digital\b",
                r"\bcloud|saas|platform\b",
                r"\bstartup.*tech|tech.*startup\b",
            ],

            "E-Commerce": [
                r"\be-commerce|ecommerce|online.*shop\b",
                r"\bamazon|ebay|shopify|zalando\b",
                r"\bonline.*handel|webshop\b",
            ],

            "Telekommunikation": [
                r"\btelekommunikation|telecommunication|telecom\b",
                r"\bmobilfunk|5g|netzwerk|network\b",
                r"\btelekom|vodafone|o2\b",
            ],

            "Fintech": [
                r"\bfintech|financial\s+technology\b",
                r"\bdigital.*bank|neobank|payment\b",
                r"\bcryptowährung|blockchain|bitcoin\b",
            ],

            "Medien & Unterhaltung (Digital)": [
                r"\bstreaming|netflix|spotify|gaming\b",
                r"\bsocial\s+media|content.*platform\b",
                r"\bdigital.*media|online.*medien\b",
            ],

            # ═══════════════════════════════════════════════════════════════
            # EBENE 2: NACE STANDARD (EU-Klassifikation)
            # ═══════════════════════════════════════════════════════════════

            # A - Land- und Forstwirtschaft
            "Landwirtschaft": [
                r"\blandwirtschaft|agriculture|farming\b",
                r"\bagrar|forstwirtschaft|forst\b",
            ],

            # B - Bergbau
            "Bergbau": [
                r"\bbergbau|mining|rohstoff\b",
                r"\btagesbau|bergwerk|förderung\b",
            ],

            # C - Verarbeitendes Gewerbe
            "Maschinenbau": [
                r"\bmaschinenbau|mechanical\s+engineering\b",
                r"\bmaschinen|anlagenbau|fertigung\b",
            ],

            "Automobilindustrie": [
                r"\bautomobil|automotive|fahrzeug\b",
                r"\bauto|kfz|pkw\b",
                r"\bbmw|mercedes|volkswagen|audi|porsche\b",
            ],

            "Chemie": [
                r"\bchemie|chemical|chemisch\b",
                r"\bbasf|bayer|kunststoff\b",
            ],

            "Lebensmittel": [
                r"\blebensmittel|food|nahrungsmittel\b",
                r"\bgetränke|beverage|ernährung\b",
            ],

            # D - Energieversorgung
            "Energieversorgung": [
                r"\benergie|energy|strom|elektrizität\b",
                r"\bkraftwerk|energieversorger|stadtwerke\b",
            ],

            # E - Wasserversorgung
            "Umwelt & Entsorgung": [
                r"\bumwelt|environment|entsorgung\b",
                r"\brecycling|abfall|waste\b",
            ],

            # F - Baugewerbe
            "Bauwesen": [
                r"\bbau|construction|bauwesen\b",
                r"\bhochbau|tiefbau|bauunternehmen\b",
            ],

            # G - Handel
            "Handel": [
                r"\bhandel|retail|einzelhandel\b",
                r"\bgroßhandel|wholesale|vertrieb\b",
            ],

            # H - Verkehr und Lagerei
            "Logistik & Transport": [
                r"\blogistik|logistics|transport\b",
                r"\bspedition|kurier|lager|warehouse\b",
                r"\bdhl|ups|fedex\b",
            ],

            # I - Gastgewerbe
            "Gastronomie & Tourismus": [
                r"\bgastronomie|restaurant|hotel\b",
                r"\btourismus|tourism|reise|travel\b",
            ],

            # J - Information und Kommunikation (teilweise Digital)
            "Medien & Verlage": [
                r"\bverlag|publishing|medien\b",
                r"\bzeitung|zeitschrift|presse|news\b",
            ],

            # K - Finanz- und Versicherungsdienstleistungen
            "Finanzdienstleistungen": [
                r"\bbank|banking|finanz|financial\b",
                r"\bversicherung|insurance|kredit\b",
                r"\bcommerzbank|deutsche\s+bank|sparkasse\b",
            ],

            # L - Grundstücks- und Wohnungswesen
            "Immobilien": [
                r"\bimmobilien|real\s+estate|property\b",
                r"\bwohnungsbau|immobilienverwaltung\b",
            ],

            # M - Freiberufliche, wissenschaftliche und technische Dienstleistungen
            "Unternehmensberatung": [
                r"\bberatung|consulting|management.*consulting\b",
                r"\bmckinsey|bcg|bain|deloitte|pwc|ey|kpmg\b",
            ],

            "Rechtsberatung": [
                r"\bkanzlei|rechtsberatung|law\s+firm\b",
                r"\banwalt|legal|jura\b",
            ],

            # N - Sonstige wirtschaftliche Dienstleistungen
            "Personaldienstleistungen": [
                r"\bpersonal|staffing|recruitment\b",
                r"\bzeitarbeit|personalvermittlung|hr.*services\b",
            ],

            # O - Öffentliche Verwaltung
            "Öffentlicher Dienst": [
                r"\böffentlich|public\s+sector|verwaltung\b",
                r"\bbehörde|amt|ministerium|regierung\b",
            ],

            # P - Erziehung und Unterricht
            "Bildung": [
                r"\bbildung|education|schule|school\b",
                r"\bunterricht|lehre|akademie|training\b",
            ],

            # Q - Gesundheits- und Sozialwesen
            "Gesundheitswesen": [
                r"\bgesundheit|healthcare|health\b",
                r"\bkrankenhaus|klinik|hospital|pflege\b",
                r"\bmedizin|medical|arzt|praxis\b",
            ],

            # R - Kunst, Unterhaltung und Erholung
            "Kultur & Unterhaltung": [
                r"\bkultur|culture|kunst|art\b",
                r"\bunterhaltung|entertainment|event\b",
            ],

            # S - Sonstige Dienstleistungen
            "Sonstige Dienstleistungen": [
                r"\bdienstleistung|service|services\b",
            ],
        }

    def _classify_with_patterns(self, text: str) -> str:
        """
        Klassifiziert mit Industrie-Patterns

        Returns:
            Spezifische Industrie oder "Sonstige Branche"
        """
        for industry, patterns in self.INDUSTRY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return industry

        return "Sonstige Branche"

    # ═══════════════════════════════════════════════════════════════════
    # DATA LOADING (7-Ebenen-Struktur)
    # ═══════════════════════════════════════════════════════════════════

    def _load_academia_industries(self) -> Dict[str, int]:
        """
        Lädt Academia Industries (Ebene 5) aus Modulhandbüchern

        Returns:
            {industry_name: level}
        """
        try:
            base_dir = Path(__file__).resolve().parents[3]
            json_path = base_dir / "data" / "modulhandbuecher" / "industries.json"

            if json_path.exists():
                with json_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return {k.lower(): 5 for k in data.keys()}
        except Exception as e:
            print(f"⚠️ Konnte Academia-Industrien nicht laden: {e}")

        # Fallback: Bekannte Academia-Branchen
        return {
            "wissenschaft & forschung": 5,
            "akademische forschung": 5,
            "grundlagenforschung": 5,
            "angewandte forschung": 5,
        }

    def _load_fachbuch_industries(self) -> Dict[str, int]:
        """
        Lädt Fachbuch Industries (Ebene 4) aus Fachliteratur

        Returns:
            {industry_name: level}
        """
        try:
            base_dir = Path(__file__).resolve().parents[3]
            json_path = base_dir / "data" / "fachbuecher" / "industries.json"

            if json_path.exists():
                with json_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return {k.lower(): 4 for k in data.keys()}
        except Exception as e:
            print(f"⚠️ Konnte Fachbuch-Industrien nicht laden: {e}")

        # Fallback: Bekannte spezialisierte Branchen
        return {
            "biotech & life sciences": 4,
            "luft- & raumfahrt": 4,
            "erneuerbare energien": 4,
            "medizintechnik": 4,
            "halbleiter": 4,
        }

    def _load_digital_industries(self) -> Dict[str, int]:
        """
        Lädt Digital Industries (Ebene 3)

        Returns:
            {industry_name: level}
        """
        return {
            "informationstechnologie": 3,
            "software": 3,
            "e-commerce": 3,
            "telekommunikation": 3,
            "fintech": 3,
            "medien & unterhaltung (digital)": 3,
            "gaming": 3,
            "cloud services": 3,
            "künstliche intelligenz": 3,
            "cybersecurity": 3,
        }

    def _load_nace_industries(self) -> Dict[str, str]:
        """
        Lädt NACE Standard Industries (Ebene 2)

        Returns:
            {company_name: nace_code}
        """
        try:
            base_dir = Path(__file__).resolve().parents[3]
            json_path = base_dir / "data" / "nace" / "company_to_nace.json"

            if not json_path.exists():
                # Fallback: Best Practice Code Lib
                json_path = base_dir / "konzept-ideen" / "Best_Practice Code Lib" / "BestPracitce_PY" / "company_to_nace.json"

            if json_path.exists():
                with json_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
        except Exception as e:
            print(f"⚠️ Konnte NACE-Daten nicht laden: {e}")

        # Fallback: Bekannte Firmen mit NACE-Codes
        return {
            "EY": "M69.2 Managementberatung",
            "KPMG": "M69.2 Managementberatung",
            "PwC": "M69.2 Managementberatung",
            "Commerzbank": "K64.1 Kreditinstitute",
            "BMW": "C29.1 Automobilindustrie",
            "Siemens": "C26 Elektroindustrie",
        }

    # ═══════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════

    def get_nace_code_for_company(self, company_name: str) -> Optional[str]:
        """
        Gibt NACE-Code für ein Unternehmen zurück

        Returns:
            NACE-Code (z.B. "M69.2 Managementberatung") oder None
        """
        for company, nace_code in self._nace_industries.items():
            if company.lower() in company_name.lower():
                return nace_code
        return None

    def get_all_industries_by_level(self) -> Dict[int, List[str]]:
        """
        Gibt alle Industrien gruppiert nach Level zurück

        Returns:
            {level: [industry_names]}
        """
        industries_by_level = {1: [], 2: [], 3: [], 4: [], 5: []}

        # Ebene 5
        industries_by_level[5] = list(self._academia_industries.keys())

        # Ebene 4
        industries_by_level[4] = list(self._fachbuch_industries.keys())

        # Ebene 3
        industries_by_level[3] = list(self._digital_industries.keys())

        # Ebene 2
        industries_by_level[2] = list(set(self._nace_industries.values()))

        return industries_by_level

    def get_industry_statistics(self) -> Dict:
        """
        Gibt Statistiken über geladene Industrien zurück

        Returns:
            {total, by_level, digital_count}
        """
        by_level = self.get_all_industries_by_level()

        return {
            "total": sum(len(industries) for industries in by_level.values()),
            "by_level": {
                f"Level {level}": len(industries)
                for level, industries in by_level.items()
            },
            "digital_count": len(self._digital_industries),
            "nace_companies": len(self._nace_industries),
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def classify_industry_from_job(job_data: Dict) -> Tuple[str, int]:
    """
    Klassifiziert Industrie aus Job-Daten

    Args:
        job_data: {title, text, company, ...}

    Returns:
        (industry_name, level)
    """
    service = IndustryService()

    industry = service.classify_industry(
        job_text=job_data.get("text", ""),
        job_title=job_data.get("title", ""),
        company_name=job_data.get("company", "")
    )

    level = service.get_industry_level(industry)

    return industry, level


if __name__ == "__main__":
    # Test
    service = IndustryService()

    print("\n" + "="*60)
    print("INDUSTRY SERVICE - TEST")
    print("="*60)

    # Test Cases
    test_jobs = [
        {"title": "Data Scientist", "text": "Machine Learning Python Forschung", "company": "Max Planck Institut"},
        {"title": "Backend Developer", "text": "Java Spring Boot Cloud AWS", "company": "Tech Startup"},
        {"title": "Unternehmensberater", "text": "Strategy Consulting", "company": "McKinsey"},
        {"title": "Ingenieur", "text": "Maschinenbau CAD Konstruktion", "company": "Siemens"},
        {"title": "Projektmanager", "text": "Automotive Fahrzeugentwicklung", "company": "BMW"},
    ]

    print("\n✓ Klassifizierung Test:")
    for job in test_jobs:
        industry = service.classify_industry(
            job_text=job["text"],
            job_title=job["title"],
            company_name=job["company"]
        )
        level = service.get_industry_level(industry)

        print(f"\n   {job['company']:20} ({job['title']})")
        print(f"   → {industry} (Level {level})")

    # Statistiken
    print("\n✓ Statistiken:")
    stats = service.get_industry_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n" + "="*60)
    print("✅ Test abgeschlossen")
    print("="*60)
