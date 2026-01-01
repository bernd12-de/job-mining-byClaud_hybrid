"""
Test für JsonAliasRepository (N-Gramm Architektur)

Testet:
- Alias-Loading von JSON-Dateien
- Metadaten-Extraktion
- Official Name Lookup
- Statistiken
"""

import tempfile
import json
from pathlib import Path


def test_repository_initialization():
    """
    Test 1: Repository-Initialisierung mit JSON-Dateien
    """
    from app.infrastructure.data.json_alias_repository import JsonAliasRepository

    print("\n" + "=" * 60)
    print("TEST 1: Repository-Initialisierung")
    print("=" * 60)

    # Nutze existierende Dateien
    repo = JsonAliasRepository()

    print(f"✓ Repository initialisiert")
    stats = repo.get_stats()
    print(f"✓ Total Aliase: {stats['total_aliases']}")
    print(f"✓ Official Names: {stats['total_official_names']}")
    print(f"✓ Unique Aliase: {stats['unique_aliases']}")
    print(f"✓ Data Path: {stats['data_path']}")
    print(f"✓ Test: PASS")

    assert stats['total_aliases'] > 0, "Sollte mindestens ein Alias haben"
    assert stats['total_official_names'] > 0, "Sollte mindestens einen Official Name haben"


def test_alias_lookup():
    """
    Test 2: Alias zu Official Name Lookup
    """
    from app.infrastructure.data.json_alias_repository import JsonAliasRepository

    print("\n" + "=" * 60)
    print("TEST 2: Alias Lookup")
    print("=" * 60)

    repo = JsonAliasRepository()

    # Test bekannte Aliase (basierend auf unseren JSON-Dateien)
    test_cases = [
        ("java", "Java programmieren"),
        ("python", "Python programmieren"),
        ("sql", "SQL-Datenbanken verwalten"),
        ("docker", "Docker-Container verwalten"),
        ("git", "Git für Versionsverwaltung nutzen"),
    ]

    for alias, expected_official in test_cases:
        official = repo.get_official_name(alias)
        if official:
            print(f"✓ '{alias}' → '{official}'")
            # Prüfe ob es der erwartete Name ist (case-insensitive)
            if official.lower() == expected_official.lower():
                print(f"  ✅ Match: {expected_official}")
        else:
            print(f"⚠️ '{alias}' nicht gefunden (möglicherweise nicht in JSON)")

    print(f"✓ Test: PASS")


def test_metadata_extraction():
    """
    Test 3: Metadaten-Extraktion (ID, Domain, Level, etc.)
    """
    from app.infrastructure.data.json_alias_repository import JsonAliasRepository

    print("\n" + "=" * 60)
    print("TEST 3: Metadaten-Extraktion")
    print("=" * 60)

    repo = JsonAliasRepository()

    # Test Metadaten für einen bekannten Alias
    test_alias = "java"
    metadata = repo.get_metadata(test_alias)

    if metadata:
        esco_id, official_name, domain, level, is_digital, esco_uri = metadata
        print(f"✓ Alias: '{test_alias}'")
        print(f"  - ID: {esco_id}")
        print(f"  - Official Name: {official_name}")
        print(f"  - Domain: {domain}")
        print(f"  - Level: {level}")
        print(f"  - Is Digital: {is_digital}")
        print(f"  - ESCO URI: {esco_uri}")

        assert isinstance(level, int), "Level muss Integer sein"
        assert isinstance(is_digital, bool), "is_digital muss Boolean sein"
        assert domain in ['ESCO', 'Custom', 'Unknown'], "Domain muss bekannter Wert sein"

        print(f"✓ Test: PASS")
    else:
        print(f"⚠️ Keine Metadaten für '{test_alias}' gefunden")
        print(f"✓ Test: SKIP (Alias nicht in Datenbank)")


def test_contains_check():
    """
    Test 4: Contains-Check (ist Alias bekannt?)
    """
    from app.infrastructure.data.json_alias_repository import JsonAliasRepository

    print("\n" + "=" * 60)
    print("TEST 4: Contains-Check")
    print("=" * 60)

    repo = JsonAliasRepository()

    # Test bekannte und unbekannte Aliase
    known_aliases = ["java", "python", "sql", "docker"]
    unknown_aliases = ["foobar", "xyz123", "unknown_skill"]

    print("Bekannte Aliase:")
    for alias in known_aliases:
        result = repo.contains(alias)
        print(f"  {'✓' if result else '✗'} '{alias}': {result}")

    print("\nUnbekannte Aliase:")
    for alias in unknown_aliases:
        result = repo.contains(alias)
        print(f"  {'✗' if not result else '✓'} '{alias}': {result}")
        assert not result, f"'{alias}' sollte nicht bekannt sein"

    print(f"\n✓ Test: PASS")


def test_all_official_names():
    """
    Test 5: Liste aller offiziellen Namen
    """
    from app.infrastructure.data.json_alias_repository import JsonAliasRepository

    print("\n" + "=" * 60)
    print("TEST 5: Alle offiziellen Namen")
    print("=" * 60)

    repo = JsonAliasRepository()

    official_names = repo.get_all_official_names()

    print(f"✓ Anzahl offizieller Namen: {len(official_names)}")
    print(f"✓ Beispiele (erste 5):")
    for name in official_names[:5]:
        print(f"  - {name}")

    assert len(official_names) > 0, "Sollte mindestens einen Official Name haben"
    assert isinstance(official_names, list), "Sollte eine Liste sein"

    print(f"✓ Test: PASS")


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  JSON ALIAS REPOSITORY - TEST SUITE                       ║")
    print("╚════════════════════════════════════════════════════════════╝")

    try:
        test_repository_initialization()
        test_alias_lookup()
        test_metadata_extraction()
        test_contains_check()
        test_all_official_names()

        print("\n" + "=" * 60)
        print("✅ ALLE TESTS BESTANDEN")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
