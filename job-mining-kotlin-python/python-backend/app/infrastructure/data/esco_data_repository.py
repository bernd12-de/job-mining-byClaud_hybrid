import pandas as pd
import os
import json
from typing import Dict, List, Any, Optional

class ESCODataRepository:
    """
    Zentrales Repository für alle ESCO-Daten.
    Verknüpft Skills mit Hierarchien, Gruppen und Collections (Digital, Research, etc.).
    """
    def __init__(self, data_path: str = "data/esco"):
        self.data_path = data_path
        self.skills: Dict[str, Dict[str, Any]] = {} # URI -> Daten-Objekt
        self.label_to_uri: Dict[str, str] = {}      # Label/Synonym -> URI
        self.approved_aliases: Dict[str, str] = {}  # term(lower) -> canonical label(lower)
        self._is_loaded = False

    def load_all(self):
        """Lädt alle ESCO-Komponenten und verknüpft sie."""
        if self._is_loaded:
            return

        print("🚀 Starte Ingestion der ESCO-Wissensbasis...")

        # 1. Haupt-Skills & Synonyme laden
        self._load_base_skills()

        # 1b. Approved Aliases (Discovery-Review) laden und integrieren
        self._load_approved_aliases()

        # 2. Hierarchien laden (Abstraktionsebene)
        self._load_hierarchies()

        # 3. Collections laden (Digitalisierung, Forschung)
        self._load_collections()

        # 4. Validierung (Integritätscheck)
        self._validate_integrity()

        self._is_loaded = True
        print(f"✅ ESCO-Wissensbasis bereit: {len(self.skills)} Konzepte geladen.")

    def _load_base_skills(self):
        """Lädt preferredLabels und altLabels aus skills_de.csv."""
        path = os.path.join(self.data_path, "skills_de.csv")
        df = pd.read_csv(path, delimiter=';') # Oder ',' je nach Export

        for _, row in df.iterrows():
            uri = row['conceptUri']
            pref_label = row['preferredLabel']
            alt_labels = str(row.get('altLabels', '')).split('|')

            skill_data = {
                "uri": uri,
                "preferredLabel": pref_label,
                "altLabels": [s.strip() for s in alt_labels if s.strip()],
                "type": row.get('conceptType', 'Skill'),
                "collections": [], # Wird später gefüllt
                "parents": []      # Wird später gefüllt
            }

            self.skills[uri] = skill_data
            self.label_to_uri[pref_label.lower()] = uri
            for alt in skill_data["altLabels"]:
                self.label_to_uri[alt.lower()] = uri

    def _load_approved_aliases(self):
        """Lädt von Discovery freigegebene Aliasse und integriert sie als Label-Mapping."""
        base = os.environ.get("BASE_DATA_DIR")
        if base:
            path = os.path.join(base, "discovery", "approved_skills.json")
        else:
            repo_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "python-backend", "data", "discovery"))
            path = os.path.join(repo_base, "approved_skills.json")

        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f) or {}
                for term, canonical in data.items():
                    t = str(term).lower().strip()
                    c = str(canonical).lower().strip()
                    if not t:
                        continue
                    self.approved_aliases[t] = c
                    uri = self.label_to_uri.get(c)
                    if uri:
                        self.label_to_uri[t] = uri
            except Exception:
                pass

    def _load_hierarchies(self):
        """Verknüpft Skills mit ihren Überordnungen (Abstraktion)."""
        path = os.path.join(self.data_path, "skillsHierarchy_de.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            for _, row in df.iterrows():
                uri = row.get('conceptUri')
                parent_uri = row.get('parentUri') # Spaltennamen ggf. anpassen
                if uri in self.skills and parent_uri:
                    self.skills[uri]["parents"].append(parent_uri)

    def _load_collections(self):
        """Markiert Skills als Digital, Green, Research, Transversal oder Language."""
        collections = {
            "digital": "digitalSkillsCollection_de.csv",
            "research": "researchSkillsCollection_de.csv",
            "transversal": "transversalSkillsCollection_de.csv",
            "language": "languageSkillsCollection_de.csv"
        }

        for key, filename in collections.items():
            path = os.path.join(self.data_path, filename)
            if os.path.exists(path):
                df = pd.read_csv(path)
                # Wir suchen flexibel nach der URI-Spalte
                uri_col = next((col for col in df.columns if 'uri' in col.lower()), 'conceptUri')
                for _, row in df.iterrows():
                    uri = row.get('conceptUri')
                    if uri in self.skills:
                        # Markiere den Skill in der zentralen Map
                        self.skills[uri]["collections"].append(key)
                        if key == "digital":
                            self.skills[uri]["is_digital"] = True

    def _validate_integrity(self):
        """Prüft auf den 558er Fehler (unvollständige Daten)."""
        if len(self.skills) < 10000:
            raise ValueError(f"CRITICAL DATA INTEGRITY ERROR: Nur {len(self.skills)} ESCO-Labels geladen!")

    # Getter für den Extractor
    def get_all_labels(self) -> List[str]:
        base_labels = set(self.label_to_uri.keys())
        base_labels.update(self.approved_aliases.keys())
        return list(base_labels)

    def get_data_by_label(self, label: str) -> Optional[Dict]:
        key = label.lower()
        uri = self.label_to_uri.get(key)
        if not uri:
            canonical = self.approved_aliases.get(key)
            if canonical:
                uri = self.label_to_uri.get(canonical)
        return self.skills.get(uri) if uri else None
