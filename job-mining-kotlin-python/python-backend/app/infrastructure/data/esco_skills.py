# esco_skills.py - ERWEITERTE VERSION

import pandas as pd
import os
from typing import Dict, List, Optional, Tuple
import json

# --- A. Konfiguration des Datenpfads ---
ESCO_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'esco')
ESCO_CACHE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'esco_labels_cache.json')
# NEU: Pfad für den erweiterten Cache, der URIs und IDs speichert
ESCO_URI_CACHE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'esco_uri_map_cache.json')
# Ermittle das Projekt-Verzeichnis (python-backend)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ESCO_DATA_PATH = os.path.join(BASE_DIR, "data", "esco")


# --- B. Direkte Zuordnung ---
ESCO_MAPPING_DATA = {
    # ... (Ihre Custom Mappings bleiben unverändert) ...
    "sql": "Datenbanken verwalten",
    "datenanalyse": "Datenanalyse-Software benutzen",
    "user experience design": "Benutzererfahrung konzipieren",
    "prototypen": "Prototyping durchführen",
    "wireframes": "Wireframes und Mock-ups erstellen",
    "teamgeist": "Teamfähigkeit demonstrieren",
    "jira": "Project-Management-Software benutzen",
    "projektmanagement": "Projektmanagement durchführen",
    "scrum": "SCRUM anwenden",
}

# --- C. Globale Caches ---
ESCO_TARGET_LABELS_CACHE: Optional[List[str]] = None
ESCO_MAPPING_CACHE: Optional[Dict[str, str]] = None
# NEU: Cache für das Mapping von Label -> (ID, URI)
ESCO_URI_MAP_CACHE: Optional[Dict[str, Tuple[str, str]]] = None


# =========================================================
# NEU: Data Integrity Threshold
# Vollständige ESCO v1.2.0 hat ca. 14.000 Skills. Wir setzen das absolute Minimum.
MIN_REQUIRED_ESCO_LABELS = 10000
# =========================================================

def _load_esco_labels_from_csv_to_cache() -> Tuple[List[str], Dict[str, Tuple[str, str]]]:
    """
    Diese Funktion parst die CSVs, erstellt den Label-Cache und den URI-Mapping-Cache.
    """
    all_labels = set()
    uri_map: Dict[str, Tuple[str, str]] = {}

    # ... (Dateisuchlogik bleibt unverändert) ...
    try:
        all_files = os.listdir(ESCO_DATA_PATH)
    except FileNotFoundError:
        print(f"❌ FEHLER: ESCO-Datenpfad nicht gefunden: {ESCO_DATA_PATH}")
        return [], {}

    skill_files = [f for f in all_files if f.endswith('.csv') and ('skill' in f.lower() or 'collection' in f.lower()) and not f.startswith('occupation')]

    for filename in skill_files:
        full_path = os.path.join(ESCO_DATA_PATH, filename)

        try:
            # ... (Robustes Lesen der CSVs bleibt unverändert) ...
            df = None
            try:
                df = pd.read_csv(full_path, delimiter=';', encoding='utf-8')
                if df.shape[1] <= 2: raise ValueError
            except Exception:
                df = pd.read_csv(full_path, delimiter=',', encoding='utf-8')

            # --- KERN-FIX: ID, URI und Label speichern ---
            preferred_term_cols = [col for col in df.columns if 'preferred term' in col.lower() or 'preferredLabel' in col]

            # WICHTIG: Die Spaltennamen für ID und URI können variieren.
            id_col = next((col for col in df.columns if 'code' in col.lower() or 'id' in col.lower()), None)
            uri_col = next((col for col in df.columns if 'uri' in col.lower()), None)

            if preferred_term_cols and id_col and uri_col:
                for col in preferred_term_cols:
                    for index, row in df.iterrows():
                        label = row[col]
                        uri = row[uri_col]
                        esco_id = row[id_col]

                        if pd.notna(label) and pd.notna(uri) and pd.notna(esco_id):
                            label_str = str(label).strip()
                            uri_str = str(uri).strip()
                            id_str = str(esco_id).strip()

                            all_labels.add(label_str)
                            # Speichert Label -> (ID, URI)
                            uri_map[label_str] = (id_str, uri_str)

        except Exception as e:
            print(f"❌ FEHLER beim Parsen von {filename}: {e}")

    # Füge Custom Mappings hinzu (ohne URI/ID, daher Platzhalter)
    for label in ESCO_MAPPING_DATA.values():
        all_labels.add(label)
        if label not in uri_map:
            # Platzhalter für Custom Skills
            uri_map[label] = ('CUSTOM_SKILL', f"esco/skill/CUSTOM_{label.replace(' ', '_')}")


    final_labels = sorted(list(all_labels))

    # =========================================================================
    # 🚨 KRITISCHER DATA INTEGRITY CHECK (QUANTITÄT)
    # =========================================================================
    if len(final_labels) < MIN_REQUIRED_ESCO_LABELS:
        error_message = (
            f"\n\n========================= 🚨 KRITISCHER DATA INTEGRITY ERROR 🚨 =========================\n"
            f"FEHLER: Es wurden nur {len(final_labels)} ESCO-Kompetenzen geladen (erwartet: mindestens {MIN_REQUIRED_ESCO_LABELS}).\n"
            f"Der Prozess wird aufgrund unvollständiger Daten gestoppt.\n"
            f"BITTE PRÜFEN SIE DEN ORDNER/DIE CSVs: '{ESCO_DATA_PATH}'\n"
            f"========================================================================================\n"
        )
        print(error_message)
        # Stoppt die weitere Ausführung des gesamten Systems
        raise ValueError(error_message)


    # 1. Schreibe den Label-Cache
    try:
        with open(ESCO_CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(final_labels, f, ensure_ascii=False)
        print(f"*** ✅ ESCO-Cache (Labels) erfolgreich erstellt: {len(final_labels)} Labels. ***")
    except Exception as e:
        print(f"❌ FEHLER beim Schreiben des ESCO-Label-Cache: {e}")

    # 2. Schreibe den URI-Map Cache
    try:
        # Konvertiere Tupel zu Liste für JSON-Serialisierung
        serializable_uri_map = {k: list(v) for k, v in uri_map.items()}
        with open(ESCO_URI_CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(serializable_uri_map, f, ensure_ascii=False)
        print(f"*** ✅ ESCO-Cache (URI Map) erfolgreich erstellt: {len(uri_map)} Einträge. ***")
    except Exception as e:
        print(f"❌ FEHLER beim Schreiben des ESCO-URI-Map Cache: {e}")

    return final_labels, uri_map


def _load_esco_data_from_cache() -> Tuple[List[str], Dict[str, Tuple[str, str]]]:
    """
    Lade ESCO-Daten: Versucht zuerst den Cache, bei Fehler wird neu geparst.
    """
    global ESCO_TARGET_LABELS_CACHE, ESCO_URI_MAP_CACHE

    # Schnell-Check der Caches
    if ESCO_TARGET_LABELS_CACHE is not None and ESCO_URI_MAP_CACHE is not None:
        return ESCO_TARGET_LABELS_CACHE, ESCO_URI_MAP_CACHE

    labels = None
    uri_map = None

    # 1. Versuch: Lade aus JSON Caches
    if os.path.exists(ESCO_CACHE_PATH) and os.path.exists(ESCO_URI_CACHE_PATH):
        try:
            with open(ESCO_CACHE_PATH, 'r', encoding='utf-8') as f:
                labels = json.load(f)

            with open(ESCO_URI_CACHE_PATH, 'r', encoding='utf-8') as f:
                # Konvertiere Liste zurück zu Tupel
                temp_map = json.load(f)
                uri_map = {k: tuple(v) for k, v in temp_map.items()}

            ESCO_TARGET_LABELS_CACHE = labels
            ESCO_URI_MAP_CACHE = uri_map

            # =========================================================================
            # 🚨 KRITISCHER DATA INTEGRITY CHECK FÜR DEN CACHE (QUANTITÄT)
            # =========================================================================
            if len(labels) < MIN_REQUIRED_ESCO_LABELS:
                error_message = (
                    f"\n\n========================= 🚨 KRITISCHER DATA INTEGRITY ERROR (CACHE) 🚨 =========================\n"
                    f"FEHLER: Der ESCO-Cache enthält nur {len(labels)} Einträge (erwartet: mindestens {MIN_REQUIRED_ESCO_LABELS}).\n"
                    f"Der Cache ist unvollständig. Starte Neuaufbau aus CSVs, um dies zu korrigieren.\n"
                    f"================================================================================================\n"
                )
                print(error_message)
                # Fällt zu Schritt 2 zurück (Neuaufbau)
                raise ValueError("Cache ist unvollständig, versuche Neuaufbau.")

            print(f"*** ✅ ESCO-Caches geladen: {len(labels)} Labels. ***")
            return labels, uri_map

        except Exception as e:
            print(f"⚠️ Warnung: Fehler beim Lesen der ESCO-Caches ({e}). Starte Neuaufbau.")
            # Fällt durch zu Schritt 2

    # 2. Versuch: Neuaufbau aus CSVs
    print("⚠️ ESCO-Caches nicht gefunden/fehlerhaft. Starte Neuaufbau aus CSVs...")
    return _load_esco_labels_from_csv_to_cache()


# --- Öffentliche Methoden ---

def get_esco_target_labels() -> List[str]:
    """Gibt die Liste aller eindeutigen, offiziellen ESCO-Labels zurück."""
    labels, _ = _load_esco_data_from_cache()
    return labels


def get_esco_mapping() -> Dict[str, str]:
    """Gibt das Mapping von Abkürzung/Synonym zu ESCO-Label zurück (unverändert)."""
    global ESCO_MAPPING_CACHE
    if ESCO_MAPPING_CACHE is None:
        ESCO_MAPPING_CACHE = ESCO_MAPPING_DATA
    return ESCO_MAPPING_CACHE


def get_esco_uri_and_id(esco_label: str) -> Tuple[Optional[str], Optional[str]]:
    """
    NEU: Gibt die ESCO URI und ID für das gegebene ESCO-Label zurück.
    Gibt (URI, ID) oder (None, None) zurück.
    """
    _, uri_map = _load_esco_data_from_cache()

    # Clean Label, um es mit dem Schlüssel im Cache abzugleichen
    clean_label = esco_label.strip()

    if clean_label in uri_map:
        esco_id, esco_uri = uri_map[clean_label]
        # Das DTO erwartet URI, dann ID. Hier kehren wir das Tupel um
        return esco_uri, esco_id

    return None, None
