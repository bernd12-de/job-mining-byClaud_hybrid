# domain/services/esco_service.py
from typing import Dict, List, Optional, Tuple
from app.infrastructure.data.esco_data_repository import ESCODataRepository

# --- Direkte Zuordnung (Bleibt als Geschäftslogik hier!) ---
ESCO_MAPPING_DATA = {
    "sql": "Datenbanken verwalten",
    "jira": "Projektmanagement durchführen",
    "scrum": "SCRUM anwenden",
}

class ESCOService:
    """
    Bietet logische ESCO-Dienste (Mapping, Label-Abruf) ohne I/O.
    """
    def __init__(self, esco_repo: ESCODataRepository):
        # Dependency Injection: Der Service erhält das Repository
        self._repo = esco_repo
        self._repo.load_data() # Initialisiert die Daten beim Start

    def get_esco_target_labels(self) -> List[str]:
        """Gibt die Liste aller eindeutigen, offiziellen ESCO-Labels zurück."""
        # Delegiert die Datenbeschaffung an das Repository
        return self._repo.get_labels()

    def get_esco_mapping(self) -> Dict[str, str]:
        """Gibt das Mapping von Abkürzung/Synonym zu ESCO-Label zurück (bleibt Geschäftslogik)."""
        return ESCO_MAPPING_DATA

    def get_esco_uri_and_id(self, esco_label: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Gibt die ESCO URI und ID für das gegebene ESCO-Label zurück.
        """
        uri_map = self._repo.get_uri_map()
        clean_label = esco_label.strip()

        if clean_label in uri_map:
            esco_id, esco_uri = uri_map[clean_label]
            # Das DTO erwartet URI, dann ID.
            return esco_uri, esco_id

        return None, None
