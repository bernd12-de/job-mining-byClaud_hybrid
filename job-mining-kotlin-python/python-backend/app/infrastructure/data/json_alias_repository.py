# app/infrastructure/data/json_alias_repository.py

import json
import os
from pathlib import Path
from typing import Dict, Tuple, Optional, List

class JsonAliasRepository:
    """
    Stellt die Datenbasis (Wörterbücher/Aliase) für das ESCO-Mapping bereit.

    ARCHITEKTUR-VORTEIL gegenüber HybridCompetenceRepository:
    - Speichert direkt Alias → (ID, Label, Domain) Metadaten
    - Kein API-Call nötig (reine JSON-Dateien)
    - Schnellere Lookups (vorberechneter Index)
    - Unterstützt N-Gramm Matching (1-3 Wörter)

    DATENFORMAT (esco_aliases.json / custom_skills_aliases.json):
    [
        {
            "id": "S1.2.3",
            "official_name": "Projektmanagement durchführen",
            "aliases": ["projektmanagement", "project management", "pm"],
            "domain": "ESCO",
            "level": 3,
            "is_digital": false,
            "esco_uri": "http://data.europa.eu/esco/skill/..."
        }
    ]
    """

    def __init__(self, data_path: Optional[Path] = None):
        """
        Initialisiert das Repository und lädt alle Alias-Dateien.

        :param data_path: Pfad zum data/competences Verzeichnis (optional)
        """
        if data_path is None:
            # Auto-detect: relativ zum Projekt-Root
            base = Path(__file__).resolve().parents[4]  # 4 Ebenen hoch: data/json_alias_repository.py -> infrastructure -> app -> python-backend -> project
            data_path = base / "data" / "competences"

        self._data_path = data_path

        # Format: {alias_lowercase: (esco_id, esco_label, domain, level, is_digital, esco_uri)}
        self._alias_metadata_map: Dict[str, Tuple[str, str, str, int, bool, str]] = {}

        # Einfaches Alias → Official Name Mapping (für Legacy-Code)
        self.all_alias_terms: Dict[str, str] = {}

        # Statistiken
        self._total_aliases = 0
        self._total_official_names = 0

        # Lade Daten
        self._load_aliases()

    def _load_aliases(self):
        """Lädt alle JSON-Dateien aus dem competences-Verzeichnis."""
        if not self._data_path.exists():
            print(f"⚠️ JsonAliasRepository: Verzeichnis {self._data_path} existiert nicht!")
            print(f"   Erstelle leeres Repository.")
            return

        # Suche nach JSON-Dateien (esco_aliases.json, custom_skills_aliases.json, etc.)
        json_files = list(self._data_path.glob("*_aliases.json"))

        if not json_files:
            print(f"⚠️ JsonAliasRepository: Keine *_aliases.json Dateien gefunden in {self._data_path}")
            return

        loaded_files = 0
        for json_file in json_files:
            try:
                with json_file.open('r', encoding='utf-8') as f:
                    data = json.load(f)

                if not isinstance(data, list):
                    print(f"⚠️ JsonAliasRepository: {json_file.name} hat ungültiges Format (erwartet Liste)")
                    continue

                for entry in data:
                    self._process_entry(entry)

                loaded_files += 1
                print(f"✅ JsonAliasRepository: {json_file.name} geladen ({len(data)} Einträge)")

            except Exception as e:
                print(f"❌ JsonAliasRepository: Fehler beim Laden von {json_file.name}: {e}")

        print(f"📊 JsonAliasRepository Statistik:")
        print(f"   - {loaded_files} Dateien geladen")
        print(f"   - {self._total_official_names} offizielle Namen")
        print(f"   - {self._total_aliases} Aliase (inkl. offizielle Namen)")

    def _process_entry(self, entry: Dict):
        """Verarbeitet einen einzelnen Eintrag aus der JSON-Datei."""
        try:
            # Pflichtfelder
            esco_id = entry.get('id', 'unknown')
            official_name = entry.get('official_name')
            aliases = entry.get('aliases', [])

            if not official_name:
                return

            # Metadaten (mit Defaults)
            domain = entry.get('domain', 'Unknown')
            level = int(entry.get('level', 3))
            is_digital = bool(entry.get('is_digital', False))
            esco_uri = entry.get('esco_uri', f'custom/{esco_id}')

            # Tuple für Metadaten
            metadata = (esco_id, official_name, domain, level, is_digital, esco_uri)

            # 1. Füge offiziellen Namen als Alias hinzu (lowercase)
            official_lower = official_name.lower().strip()
            self._alias_metadata_map[official_lower] = metadata
            self.all_alias_terms[official_lower] = official_name

            # 2. Füge alle Aliase hinzu
            for alias in aliases:
                if not alias:
                    continue
                alias_lower = alias.lower().strip()

                # Prüfe auf Duplikate (First-Wins-Strategie)
                if alias_lower in self._alias_metadata_map:
                    # Bereits vorhanden - Skip (bevorzuge erste Definition)
                    continue

                self._alias_metadata_map[alias_lower] = metadata
                self.all_alias_terms[alias_lower] = official_name

            self._total_official_names += 1
            self._total_aliases += (1 + len(aliases))  # Official + Aliases

        except Exception as e:
            print(f"⚠️ JsonAliasRepository: Fehler bei Entry {entry.get('id', '?')}: {e}")

    # --- PUBLIC API ---

    def get_all_aliases(self) -> Dict[str, Tuple[str, str, str, int, bool, str]]:
        """
        Gibt alle Aliase mit vollständigen Metadaten zurück.

        :return: Dict[alias_lowercase, (id, official_name, domain, level, is_digital, esco_uri)]
        """
        return self._alias_metadata_map

    def get_all_alias_terms(self) -> Dict[str, str]:
        """
        Gibt einfaches Alias → Official Name Mapping zurück (Legacy-Kompatibilität).

        :return: Dict[alias_lowercase, official_name]
        """
        return self.all_alias_terms

    def get_official_name(self, alias: str) -> Optional[str]:
        """
        Konvertiert einen Alias zu seinem offiziellen Namen.

        :param alias: Suchbegriff (z.B. "pm", "projektmanagement")
        :return: Offizieller Name (z.B. "Projektmanagement durchführen") oder None
        """
        if not alias:
            return None

        alias_lower = alias.lower().strip()

        # Direct lookup
        if alias_lower in self.all_alias_terms:
            return self.all_alias_terms[alias_lower]

        return None

    def get_metadata(self, alias: str) -> Optional[Tuple[str, str, str, int, bool, str]]:
        """
        Holt vollständige Metadaten für einen Alias.

        :param alias: Suchbegriff
        :return: (id, official_name, domain, level, is_digital, esco_uri) oder None
        """
        if not alias:
            return None

        alias_lower = alias.lower().strip()
        return self._alias_metadata_map.get(alias_lower)

    def lookup_with_metadata(self, term: str) -> Optional[Dict]:
        """
        Sucht einen Term und gibt ein vollständiges Metadaten-Dict zurück (API-kompatibel).

        :param term: Suchbegriff
        :return: Dict mit allen Metadaten oder None
        """
        metadata = self.get_metadata(term)
        if not metadata:
            return None

        esco_id, official_name, domain, level, is_digital, esco_uri = metadata

        return {
            'id': esco_id,
            'official_name': official_name,
            'preferredLabel': official_name,  # ESCO-Kompatibilität
            'domain': domain,
            'level': level,
            'is_digital': is_digital,
            'uri': esco_uri,
            'esco_uri': esco_uri
        }

    def get_all_official_names(self) -> List[str]:
        """
        Gibt alle offiziellen Namen zurück (ohne Duplikate).

        :return: Liste aller offiziellen ESCO-Namen
        """
        # Extrahiere official_name aus allen Metadaten (Set für Deduplizierung)
        return list({metadata[1] for metadata in self._alias_metadata_map.values()})

    def contains(self, term: str) -> bool:
        """
        Prüft, ob ein Term (Alias oder Official Name) bekannt ist.

        :param term: Suchbegriff
        :return: True wenn bekannt, sonst False
        """
        if not term:
            return False
        return term.lower().strip() in self._alias_metadata_map

    def get_stats(self) -> Dict:
        """Gibt Repository-Statistiken zurück (für Debugging)."""
        return {
            'total_aliases': self._total_aliases,
            'total_official_names': self._total_official_names,
            'unique_aliases': len(self._alias_metadata_map),
            'data_path': str(self._data_path)
        }
