# scripts/propose_new_skills.py
import requests
import json

def suggest_discovery_to_kotlin(discovery_dto, kotlin_url="http://localhost:8080"):
    """Sendet eine neue Entdeckung an den Kotlin-Datenwächter."""
    payload = {
        "label": discovery_dto.original_term,
        "uri": discovery_dto.esco_uri,
        "level": discovery_dto.level,
        "isDigital": discovery_dto.is_digital,
        "source": discovery_dto.source_domain
    }

    try:
        response = requests.post(f"{kotlin_url}/api/v1/rules/propose-skill", json=payload, timeout=5)
        if response.status_code == 201:
            print(f"✅ Skill '{discovery_dto.original_term}' erfolgreich vorgeschlagen.")
        else:
            print(f"⚠️ Kotlin lehnte Vorschlag ab: {response.status_code}")
    except Exception as e:
        print(f"❌ Verbindung zu Kotlin fehlgeschlagen: {e}")
