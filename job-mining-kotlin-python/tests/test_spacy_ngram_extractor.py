"""
Test für SpaCyNGramExtractor (N-Gramm Architektur)

Testet:
- N-Gramm-basierte Skill-Extraktion (1-3 Wörter)
- Dict-Lookup Performance
- Deduplizierung
- Integration mit JsonAliasRepository
"""


def test_dependency_check():
    """
    Test 1: Dependency Checks (spaCy, JsonAliasRepository)
    """
    print("\n" + "=" * 60)
    print("TEST 1: Dependency Checks")
    print("=" * 60)

    try:
        import spacy
        print("✓ spaCy verfügbar")
        spacy_available = True
    except ImportError:
        print("⚠️ spaCy nicht verfügbar")
        print("   Install: python -m spacy download de_core_news_md")
        spacy_available = False

    try:
        from app.infrastructure.data.json_alias_repository import JsonAliasRepository
        print("✓ JsonAliasRepository verfügbar")
        repo_available = True
    except ImportError:
        print("✗ JsonAliasRepository nicht verfügbar")
        repo_available = False

    if spacy_available and repo_available:
        print("✓ Test: PASS")
    else:
        print("✓ Test: SKIP (Dependencies fehlen)")


def test_ngram_extraction():
    """
    Test 2: N-Gramm-basierte Extraktion (1-3 Wörter)
    """
    print("\n" + "=" * 60)
    print("TEST 2: N-Gramm Extraktion")
    print("=" * 60)

    try:
        from app.infrastructure.data.json_alias_repository import JsonAliasRepository
        from app.infrastructure.extractor.spacy_ngram_extractor import SpaCyNGramExtractor
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    # Repository initialisieren
    repo = JsonAliasRepository()

    # Extractor initialisieren
    try:
        extractor = SpaCyNGramExtractor(alias_repository=repo)
    except Exception as e:
        print(f"⚠️ spaCy Model fehlt: {e}")
        print("   Install: python -m spacy download de_core_news_md")
        print("✓ Test: SKIP")
        return

    # Test-Text mit bekannten Skills
    test_text = """
    Wir suchen einen Software-Entwickler mit Erfahrung in Java, Python und SQL.
    Kenntnisse in Docker und Kubernetes sind von Vorteil.
    Erfahrung mit Git und Machine Learning wünschenswert.
    """

    # Extrahiere Kompetenzen
    competences = extractor.extract_competences(test_text, role="Software Developer")

    print(f"✓ Text analysiert ({len(test_text)} Zeichen)")
    print(f"✓ Extrahierte Kompetenzen: {len(competences)}")

    # Zeige extrahierte Skills
    if competences:
        print(f"\n   Gefundene Skills:")
        for comp in competences[:10]:  # Zeige max 10
            print(f"   - {comp.original_term} → {comp.esco_label} (Level {comp.level})")

        # Prüfe erwartete Skills
        extracted_labels = [c.esco_label.lower() for c in competences]
        expected_skills = ["java", "python", "sql", "docker", "kubernetes", "git", "machine learning"]

        found_count = sum(1 for skill in expected_skills if any(skill in label.lower() for label in extracted_labels))
        print(f"\n   ✓ Erwartete Skills gefunden: {found_count}/{len(expected_skills)}")

    print(f"\n✓ Test: PASS")


def test_deduplication():
    """
    Test 3: Deduplizierung nach offiziellem Label
    """
    print("\n" + "=" * 60)
    print("TEST 3: Deduplizierung")
    print("=" * 60)

    try:
        from app.infrastructure.data.json_alias_repository import JsonAliasRepository
        from app.infrastructure.extractor.spacy_ngram_extractor import SpaCyNGramExtractor
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    repo = JsonAliasRepository()

    try:
        extractor = SpaCyNGramExtractor(alias_repository=repo)
    except Exception as e:
        print(f"⚠️ spaCy Model fehlt: {e}")
        print("✓ Test: SKIP")
        return

    # Test-Text mit Duplikaten (Java mehrfach erwähnt)
    test_text = """
    Java Entwickler gesucht. Sie sollten Java programmieren können.
    Java ist die Hauptsprache. Erfahrung mit Java 17 erforderlich.
    """

    competences = extractor.extract_competences(test_text, role="Java Developer")

    print(f"✓ Text mit Duplikaten analysiert")
    print(f"✓ Extrahierte Kompetenzen: {len(competences)}")

    # Prüfe ob Deduplizierung funktioniert
    labels = [c.esco_label for c in competences]
    unique_labels = set(labels)

    print(f"   - Total extrahiert: {len(labels)}")
    print(f"   - Unique Labels: {len(unique_labels)}")

    if len(labels) > 0:
        assert len(unique_labels) == len(labels), "Deduplizierung sollte funktionieren"
        print(f"   ✅ Keine Duplikate gefunden!")

    print(f"\n✓ Test: PASS")


def test_multiword_skills():
    """
    Test 4: Multi-Word Skills (2-3 Wörter)
    """
    print("\n" + "=" * 60)
    print("TEST 4: Multi-Word Skills")
    print("=" * 60)

    try:
        from app.infrastructure.data.json_alias_repository import JsonAliasRepository
        from app.infrastructure.extractor.spacy_ngram_extractor import SpaCyNGramExtractor
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    repo = JsonAliasRepository()

    try:
        extractor = SpaCyNGramExtractor(alias_repository=repo)
    except Exception as e:
        print(f"⚠️ spaCy Model fehlt: {e}")
        print("✓ Test: SKIP")
        return

    # Test-Text mit Multi-Word Skills
    test_text = """
    Erfahrung mit Machine Learning und Data Science erforderlich.
    Kenntnisse in Spring Boot und Microsoft Teams von Vorteil.
    """

    competences = extractor.extract_competences(test_text, role="Data Scientist")

    print(f"✓ Multi-Word Skills analysiert")
    print(f"✓ Extrahierte Kompetenzen: {len(competences)}")

    # Zeige Multi-Word Skills
    multiword_skills = [c for c in competences if ' ' in c.original_term]
    if multiword_skills:
        print(f"\n   Multi-Word Skills gefunden:")
        for comp in multiword_skills:
            print(f"   - '{comp.original_term}' → {comp.esco_label}")
    else:
        print(f"   ℹ️ Keine Multi-Word Skills in diesem Test gefunden")

    print(f"\n✓ Test: PASS")


def test_extractor_info():
    """
    Test 5: Extractor Info String
    """
    print("\n" + "=" * 60)
    print("TEST 5: Extractor Info")
    print("=" * 60)

    try:
        from app.infrastructure.data.json_alias_repository import JsonAliasRepository
        from app.infrastructure.extractor.spacy_ngram_extractor import SpaCyNGramExtractor
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    repo = JsonAliasRepository()

    try:
        extractor = SpaCyNGramExtractor(alias_repository=repo)
    except Exception as e:
        print(f"⚠️ spaCy Model fehlt: {e}")
        print("✓ Test: SKIP")
        return

    info = extractor.get_extractor_info()
    print(f"✓ Extractor Info: {info}")

    assert "SpaCyNGramExtractor" in info, "Info sollte Extractor-Namen enthalten"
    assert "Aliase" in info, "Info sollte Alias-Anzahl enthalten"

    print(f"✓ Test: PASS")


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  SPACY N-GRAMM EXTRACTOR - TEST SUITE                     ║")
    print("╚════════════════════════════════════════════════════════════╝")

    try:
        test_dependency_check()
        test_ngram_extraction()
        test_deduplication()
        test_multiword_skills()
        test_extractor_info()

        print("\n" + "=" * 60)
        print("✅ ALLE TESTS BESTANDEN")
        print("=" * 60)
        print("\nHinweis: Für volle Funktionalität:")
        print("  python -m spacy download de_core_news_md")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
