import sys
import os
from typing import Dict, Any

# Pfad-Hacking, damit das Skript die 'app'-Module findet
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.domain.models import CompetenceDTO
from app.core.constants import JOB_CATEGORY_PATTERNS # Falls du die Datei schon angelegt hast

def validate_python_to_kotlin_contract(data: Dict[str, Any]) -> bool:
    """
    Prüft, ob die Python-Datenobjekte exakt dem 'Vertrag' mit dem
    Kotlin-Backend entsprechen (Datentypen, Pflichtfelder).
    """
    try:
        # Pydantic erzwingt hier die Typkonvertierung (z.B. String "4" zu Int 4)
        dto = CompetenceDTO(**data)

        # Zusätzliche wissenschaftliche Validierung für die Masterarbeit
        if dto.level < 1 or dto.level > 5:
            print(f"❌ VALIDIERUNGSFEHLER: Level {dto.level} ist außerhalb von Ebene 1-5.")
            return False

        print(f"✅ KONTRAKT-CHECK ERFOLGREICH: '{dto.original_term}' ist bereit für Kotlin.")
        return True

    except Exception as e:
        print(f"🚨 KONTRAKT-BRUCH GEFUNDEN!")
        print(f"Details: {str(e)}")
        return False

if __name__ == "__main__":
    # Test-Szenario 1: Ein typischer Fund aus einem Fachbuch (Ebene 4)
    test_case_success = {
        "original_term": "Microservices",
        "esco_label": "Softwarearchitektur",
        "esco_uri": "http://data.europa.eu/esco/skill/architecture",
        "confidence_score": 0.95,
        "level": "4",  # Pydantic korrigiert diesen String zu Int
        "is_digital": True,
        "source_domain": "Wolff_Microservices.pdf"
    }

    # Test-Szenario 2: Fehlerhafter Datensatz (Fehlendes Pflichtfeld)
    test_case_fail = {
        "original_term": "Fehler-Test",
        # 'esco_label' fehlt hier absichtlich
        "level": 2
    }

    print("--- Starte Integration-Test: Python-Kotlin-Contract ---")

    success = validate_python_to_kotlin_contract(test_case_success)
    failure = not validate_python_to_kotlin_contract(test_case_fail)

    if success and failure:
        print("\n🏆 Alle Contract-Tests bestanden. Python-Seite ist gesichert.")
        sys.exit(0)
    else:
        print("\n❌ Fehler in der Contract-Validierung entdeckt.")
        sys.exit(1)
