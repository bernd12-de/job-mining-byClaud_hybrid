import requests
import os
import json
import pandas as pd
from typing import Set, List, Dict
from tqdm import tqdm

# ZENTRALISIERUNG: Wir nutzen die Konstante aus deiner constants.py
try:
    from app.core.constants import DEFAULT_KOTLIN_URL
except ImportError:
    DEFAULT_KOTLIN_URL = os.environ.get("KOTLIN_API_URL", "http://localhost:8080")

class KotlinRuleClient:
    """
    Adapter (Client) für die Abfrage von Domänenregeln
    (Blacklist, Mappings, ESCO) vom Kotlin DomainRuleService.
    Inkl. robustem File-System-Fallback.
    """

    def __init__(self, base_url=None):
        # 1. FIX: Nimm die URL, die übergeben wird. Wenn keine da ist, nimm Environment/Default.
        self.base_url = base_url if base_url else DEFAULT_KOTLIN_URL
        self.fallback_path = "data/fallback_rules"
        self.esco_source = "data/esco"

        # Sicherstellen, dass der Fallback-Ordner existiert
        try:
            os.makedirs(self.fallback_path, exist_ok=True)
        except Exception as e:
            print(f"⚠️ Warnung: Konnte Fallback-Ordner nicht erstellen: {e}")
        
        print(f"🔗 KotlinRuleClient initialisiert. Basis-URL: {self.base_url}")

    def get_esco_full(self):
        endpoint = f"{self.base_url}/api/v1/rules/esco-full"
        filename = "esco_fallback.json"

        try:
            print(f"🔄 Lade ESCO-Daten von: {endpoint}")
            response = requests.get(endpoint, timeout=15)
            response.raise_for_status()

            raw_data = response.json()

            # --- 🕵️‍♂️ DEBUGGING START ---
            print(f"   🔍 DEBUG-INFO:")
            print(f"   👉 HTTP Status: {response.status_code}")
            print(f"   👉 Datentyp: {type(raw_data)}")

            if isinstance(raw_data, list):
                print(f"   👉 Anzahl Elemente: {len(raw_data)}")
                if len(raw_data) == 0:
                    print("   ⚠️ ACHTUNG: Die Liste von Kotlin ist LEER!")
                else:
                    print(f"   👉 Probe (Erstes Element): {raw_data[0]}")
                    # Zeige die Keys des ersten Elements, um Tippfehler zu finden
                    if isinstance(raw_data[0], dict):
                        print(f"   👉 Verfügbare Keys: {list(raw_data[0].keys())}")
            elif isinstance(raw_data, dict):
                print(f"   ⚠️ ACHTUNG: Habe Dictionary statt Liste erhalten. Keys: {list(raw_data.keys())}")
            else:
                print(f"   ⚠️ ACHTUNG: Unerwartetes Format: {raw_data}")
            # --- 🕵️‍♂️ DEBUGGING ENDE ---



            # 1. FIX: Liste VOR der Schleife initialisieren!
            normalized = []

            # 2. FIX: tqdm hier nutzen
            # Hinweis: Wenn du tqdm hier nutzt, brauchst du es im Repository eigentlich nicht mehr,
            # aber doppelt hält besser (oder du entfernst es dort).
            from tqdm import tqdm

            for item in tqdm(raw_data, desc="🚀 Lade Skills (Client)", unit=" sk", ncols=100):
                # Prüfen auf Label
                label = item.get("preferredLabel") or item.get("label") or item.get("esco_label")

                if label:
                    # 3. FIX: .append() nutzen statt überschreiben (=)
                    # 4. FIX: Duplikat-Felder digital/is_digital vereinheitlichen
                    normalized.append({
                        "label": label,
                        "uri": item.get("esco_uri") or item.get("uri"),
                        "is_digital": item.get("is_digital") or item.get("digital", False),
                        "level": item.get("level", 2)
                    })

            print(f"✅ {len(normalized)} Skills geladen & normalisiert.")

            # Cache speichern
            self._save_to_json(filename, normalized)
            return normalized

        except (requests.exceptions.RequestException, ConnectionError) as e:
            print(f"❌ API-Fehler bei ESCO ({e}). Versuche Fallback-Datei...")
            return self._load_or_create_fallback(filename, generation_method=self._generate_esco_from_csv)


    def fetch_blacklist(self) -> Set[str]:
        """Holt Blacklist. Fallback: JSON Datei (erstellt aus Defaults)."""
        endpoint = f"{self.base_url}/api/v1/rules/blacklist"
        filename = "blacklist_fallback.json"

        try:
            response = requests.get(endpoint, timeout=5)
            response.raise_for_status()
            data = response.json()
            # Cache update
            try:
                self._save_to_json(filename, data)
            except Exception as e:
                print(f"⚠️ Warnung: Cache-Speicherung fehlgeschlagen: {e}")
            return set(data)
        except (requests.exceptions.RequestException, ConnectionError, TimeoutError) as e:
            print(f"❌ API-Fehler bei Blacklist: {e}")
            # Nutzt _get_static_fallback_blacklist_as_list zur Generierung der Datei, falls sie fehlt
            try:
                data = self._load_or_create_fallback(filename, generation_method=self._get_static_fallback_blacklist_as_list)
                return set(data) if data else set()
            except Exception as e:
                print(f"❌ Fallback-Laden fehlgeschlagen: {e}")
                return set()

    def fetch_role_mappings(self) -> Dict[str, str]:
        """Holt Rollen-Mappings."""
        endpoint = f"{self.base_url}/api/v1/rules/role-mappings"
        filename = "role_mappings_fallback.json"

        try:
            response = requests.get(endpoint, timeout=5)
            response.raise_for_status()
            data = response.json()
            try:
                self._save_to_json(filename, data)
            except Exception as e:
                print(f"⚠️ Warnung: Cache-Speicherung fehlgeschlagen: {e}")
            return data
        except (requests.exceptions.RequestException, ConnectionError, TimeoutError) as e:
            print(f"❌ API-Fehler bei Role-Mappings: {e}")
            try:
                return self._load_or_create_fallback(filename, generation_method=self._get_static_fallback_role_mappings)
            except Exception as e:
                print(f"❌ Fallback-Laden fehlgeschlagen: {e}")
                return {}

    def fetch_industry_mappings(self) -> Dict[str, str]:
        """Holt Branchen-Mappings."""
        endpoint = f"{self.base_url}/api/v1/rules/industry-mappings"
        filename = "industry_mappings_fallback.json"

        try:
            response = requests.get(endpoint, timeout=5)
            response.raise_for_status()
            data = response.json()
            try:
                self._save_to_json(filename, data)
            except Exception as e:
                print(f"⚠️ Warnung: Cache-Speicherung fehlgeschlagen: {e}")
            return data
        except (requests.exceptions.RequestException, ConnectionError, TimeoutError) as e:
            print(f"❌ API-Fehler bei Industry-Mappings: {e}")
            try:
                return self._load_or_create_fallback(filename, generation_method=self._get_static_fallback_industry_mappings)
            except Exception as e:
                print(f"❌ Fallback-Laden fehlgeschlagen: {e}")
                return {}

    # --- HELPER & GENERATOREN ---

    def _load_or_create_fallback(self, filename, generation_method):
        """
        Generische Methode: Prüft ob Datei existiert.
        Wenn nicht: Ruft generation_method() auf und speichert das Ergebnis.
        Dann: Lädt Datei.
        """
        path = os.path.join(self.fallback_path, filename)
        print(f"⚠️ in Load or Create Fallback-Datei {filename} mit {path}. ")
        # 1. Wenn Datei nicht da, generieren wir sie EINMALIG
        if not os.path.exists(path):
            print(f"⚠️ Fallback-Datei {filename} fehlt. Erstelle sie neu...")
            data = generation_method()
            self._save_to_json(filename, data)

        # 2. Datei laden
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    print(f"   -> Lade lokalen Fallback: {filename}")
                    #return json.load(f)
                    # SCHRITT A: Daten erst in eine Variable laden
                    data = json.load(f)

                    # SCHRITT B: Test-Ausgabe (Nur die ersten paar, damit das Terminal nicht explodiert)
                    print(f"   👀 DEBUG-CHECK: {type(data)}")

                    if isinstance(data, list):
                        print(f"   📊 Anzahl Einträge: {len(data)}")
                        if data:
                            print(f"   liefere Probe (Erster Eintrag): {data[0]}")
                    elif isinstance(data, dict):
                        print(f"   📊 Anzahl Keys: {len(data)}")
                        # Zeige die ersten 2 Einträge als Probe
                        first_two = list(data.items())[:2]
                        print(f"   liefere Probe: {first_two}")

                    # SCHRITT C: Daten zurückgeben
                    return data
            except Exception as e:
                print(f"❌ Fehler beim Lesen von {path}: {e}")

        return {} # Notfall-Return

    def _load_fallback_esco(self, cache_file: str) -> Dict:
        """Lädt Fallback-Daten robust."""

        # 1. Versuche Cache-Datei (schnell)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                print(f"📂 Fallback: Cache geladen ({len(data)} Skills).")
                return data
            except json.JSONDecodeError:
                print("❌ Cache-Datei korrupt.")

        # 2. Versuche CSV-Generator (langsam, aber rettet den Start)
        print("⚙️ Fallback: Generiere aus lokalen CSV-Dateien...")
        return self._generate_esco_from_csv(cache_file)

    def _save_to_json(self, filename, data):
        path = os.path.join(self.fallback_path, filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Konnte Fallback {filename} nicht speichern: {e}")

    # --- DATEN-QUELLEN FÜR GENERIERUNG ---

    def _generate_esco_from_csv(self):
        """Liest CSVs und baut das JSON-Objekt."""
        fallback_list = []
        csv_file = os.path.join(self.esco_source, "skills.csv")
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file, usecols=['preferredLabel', 'conceptUri'])
                for _, row in tqdm(df.iterrows(),desc="🚀 Indiziere Skills", unit=" sk", ncols=100):
                    fallback_list.append({
                        "label": str(row['preferredLabel']),
                        "uri": row['conceptUri'],
                        "is_digital": False
                    })
            except Exception: pass
        return fallback_list

    def _get_static_fallback_blacklist_as_list(self):
        return list({
            "kenntnisse", "fähigkeiten", "kommunikation", "deutsch", "englisch",
            "team", "analyse", "projektleitung", "erfahrung",
            "und", "oder", "bei", "mit", "job", "suche"
        })

    def _get_static_fallback_industry_mappings(self) -> Dict[str, str]:
        return {
            'Informationstechnologie': 'IT|Software|Entwicklung|Cloud',
            'Finanzen': 'Bank|Versicherung|Finance',
            'Gesundheit': 'Pflege|Klinik|Medizin'
        }

    def _get_static_fallback_role_mappings(self) -> Dict[str, str]:
        return {
            'Entwickler': 'Developer|Software Engineer|Programmierer',
            'Manager': 'Leiter|Head of|Lead'
        }

    def _get_static_fallback_blacklist(self) -> Set[str]:
        """
        Statischer Fallback: Falls die DB/API nicht erreichbar ist, nutzen wir die
        bekannte Version, um Rauschen zu vermeiden. (Resilienz-Fallback)
        """
        print("⚠️ FALLBACK AKTIVIERT: Blacklist wird statisch geladen (DB/API nicht erreichbar).")
        return {
            "kenntnisse", "fähigkeiten", "kommunikation", "deutsch", "englisch",
            "r", "bau", "ski", "sport", "medien", "wissenschaft", "erfahrung",
            "agil", "strategie", "prozess", "management", "analyse", "projektleitung",
            "kunden", "lösung", "team", "technik", "bereich", "verantwortung übernehmen",
            "beratung", "dienstleistungen", "informatik", "digitalisierung",
            "prägen", "datenschutz", "ethik", "gesundheit", "kommunizieren", "agiles"
        }

    # NEU: Resilienz-Fallback für Branchen-Mappings
    def _get_static_fallback_industry_mappings(self) -> Dict[str, str]:
        print("⚠️ FALLBACK AKTIVIERT: Branchen-Mappings werden statisch geladen.")
        # Diese statischen Mappings ersetzen die Logik aus organization_extractor.py
        return {
            'Informationstechnologie & Software': 'IT|Software|Entwicklung|DevOps|Cloud|Informatik|Digitalisierung',
            'Finanzen & Versicherungen': 'Finanz|Bank|Versicherung|Aktie|Treasury|Bilanz',
            'Automobil & Maschinenbau': 'Automobil|Maschinenbau|Fertigung|Produktion|Anlage|Konstruktion',
            'Gesundheit & Soziales': 'Klinik|Pflege|Sozial|Heim|Therapie|Krankenhaus',
            'Handel & Logistik': 'Handel|Logistik|Einzelhandel|Lager|Supply Chain',
            'Unbekannt/Generell': 'Marketing|Vertrieb|Verwaltung|Assistenz'
        }

    # NEU: Resilienz-Fallback für Rollen-Mappings
    def _get_static_fallback_role_mappings(self) -> Dict[str, str]:
        print("⚠️ FALLBACK AKTIVIERT: Rollen-Mappings werden statisch geladen.")
        return {
            'Software-Entwicklung': 'Entwickler|Developer|Programmierer|Coding|Frontend|Backend',
            'Data & Analytics': 'Data Scientist|Analyst|BI|Statistik',
            'Projektmanagement': 'Projektleiter|Scrum Master|Product Owner',
            'Führungskraft/Management': 'Leiter|Manager|Head of',
            'Unbekannt/Generell': 'Assistent|Kauffrau|Admin'
        }



