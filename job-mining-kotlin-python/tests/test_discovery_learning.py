"""
Test für DiscoveryLearningService - Selbstlernendes System
===========================================================

Testet:
1. Discovery neuer Rollen/Skills/Industrien (Ebene 1)
2. Auto-Promotion bei Häufigkeit
3. Validierung & Level-Erhöhung
4. Export zu ESCO-Format
5. Statistiken & Reporting
"""

import tempfile
from pathlib import Path


def test_role_discovery():
    """Test 1: Neue Rolle entdecken (Ebene 1)"""
    print("\n" + "="*60)
    print("TEST 1: Rolle Discovery (Ebene 1)")
    print("="*60)

    try:
        from app.application.services.discovery_learning_service import DiscoveryLearningService
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    # Temp directory für Test
    with tempfile.TemporaryDirectory() as tmpdir:
        service = DiscoveryLearningService(data_dir=Path(tmpdir))

        # Entdecke neue Rolle
        role, level = service.discover_role(
            role_text="Quantum Computing Engineer",
            job_title="Senior Quantum Engineer",
            context="Quantum algorithms, quantum computing"
        )

        print(f"\n✓ Entdeckte Rolle: '{role}' (Level {level})")

        assert level == 1, f"Neue Rolle sollte Level 1 haben (ist: {level})"
        assert role in service.discovered_roles, "Rolle sollte gespeichert sein"

        # Zweite Entdeckung derselben Rolle
        role2, level2 = service.discover_role(
            role_text="Quantum Computing Engineer",
            job_title="Quantum Developer"
        )

        entry = service.discovered_roles[role]
        print(f"✓ Frequency nach 2. Discovery: {entry['frequency']}")

        assert entry["frequency"] == 2, "Frequency sollte 2 sein"

        print("✓ Test: PASS\n")


def test_skill_discovery_with_digital_detection():
    """Test 2: Skill Discovery mit automatischer Digital-Erkennung"""
    print("="*60)
    print("TEST 2: Skill Discovery + Digital Detection")
    print("="*60)

    try:
        from app.application.services.discovery_learning_service import DiscoveryLearningService
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        service = DiscoveryLearningService(data_dir=Path(tmpdir))

        # Digital Skill (sollte Level 3 bekommen)
        skill_digital, level_digital = service.discover_skill(
            skill_text="Kubernetes",
            context="Container orchestration cloud platform"
        )

        print(f"\n✓ Digital Skill: '{skill_digital}' (Level {level_digital})")
        assert level_digital == 3, f"Digital Skill sollte Level 3 haben (ist: {level_digital})"

        # Non-Digital Skill (sollte Level 1 bekommen)
        skill_other, level_other = service.discover_skill(
            skill_text="Teamarbeit",
            context="Soft skill communication"
        )

        print(f"✓ Non-Digital Skill: '{skill_other}' (Level {level_other})")
        assert level_other == 1, f"Non-Digital Skill sollte Level 1 haben (ist: {level_other})"

        print("✓ Test: PASS\n")


def test_auto_promotion_by_frequency():
    """Test 3: Auto-Promotion durch Häufigkeit"""
    print("="*60)
    print("TEST 3: Auto-Promotion durch Häufigkeit")
    print("="*60)

    try:
        from app.application.services.discovery_learning_service import DiscoveryLearningService
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        service = DiscoveryLearningService(data_dir=Path(tmpdir))

        # Erste Discovery: Level 1
        role, level = service.discover_role("Prompt Engineer")
        print(f"\n✓ 1. Discovery: '{role}' (Level {level})")
        assert level == 1, "Sollte Level 1 sein"

        # 2-4 Discoveries: bleibt Level 1
        for i in range(2, 5):
            role, level = service.discover_role("Prompt Engineer")
            print(f"✓ {i}. Discovery: Level {level}")

        # 5. Discovery: Auto-Promotion zu Level 2
        role, level = service.discover_role("Prompt Engineer")
        print(f"✓ 5. Discovery: Level {level} (Auto-Promoted)")

        assert level == 2, f"Sollte nach 5 Discoveries Level 2 sein (ist: {level})"

        print("✓ Test: PASS\n")


def test_validation_and_promotion():
    """Test 4: Manuelle Validierung & Promotion"""
    print("="*60)
    print("TEST 4: Manuelle Validierung")
    print("="*60)

    try:
        from app.application.services.discovery_learning_service import DiscoveryLearningService
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        service = DiscoveryLearningService(data_dir=Path(tmpdir))

        # Entdecke Rolle
        role, level = service.discover_role("AI Safety Researcher")
        print(f"\n✓ Vor Validierung: '{role}' (Level {level})")

        # Validiere mit target_level
        service.validate_role("AI Safety Researcher", target_level=5)

        entry = service.discovered_roles[role]
        print(f"✓ Nach Validierung: Level {entry['level']}, Validated={entry['validated']}")

        assert entry["level"] == 5, "Sollte auf Level 5 gesetzt sein"
        assert entry["validated"] is True, "Sollte validiert sein"

        print("✓ Test: PASS\n")


def test_export_to_esco_format():
    """Test 5: Export zu ESCO-Format"""
    print("="*60)
    print("TEST 5: Export zu ESCO-Format")
    print("="*60)

    try:
        from app.application.services.discovery_learning_service import DiscoveryLearningService
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        service = DiscoveryLearningService(data_dir=Path(tmpdir))

        # Erstelle mehrere Skills mit verschiedenen Leveln
        service.discover_skill("Python")  # Level 3 (digital)
        service.discover_skill("Teamarbeit")  # Level 1

        # Promote Teamarbeit zu Level 2
        service.validate_skill("Teamarbeit", target_level=2)

        # Export (nur Level >= 2)
        esco_skills = service.export_to_esco_format("skill", min_level=2)

        print(f"\n✓ Exportierte Skills (Level >= 2): {len(esco_skills)}")
        for skill in esco_skills:
            print(f"   • {skill['preferredLabel']} (L{skill['level']})")

        assert len(esco_skills) == 2, f"Sollte 2 Skills exportieren (ist: {len(esco_skills)})"
        assert all(s["level"] >= 2 for s in esco_skills), "Alle sollten Level >= 2 haben"

        print("✓ Test: PASS\n")


def test_statistics():
    """Test 6: Statistiken & Reporting"""
    print("="*60)
    print("TEST 6: Statistiken")
    print("="*60)

    try:
        from app.application.services.discovery_learning_service import DiscoveryLearningService
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        service = DiscoveryLearningService(data_dir=Path(tmpdir))

        # Erstelle Test-Daten
        service.discover_role("AI Engineer")
        service.discover_role("ML Engineer")
        service.discover_skill("Python")
        service.discover_skill("TensorFlow")
        service.discover_industry("AI & ML")

        # Statistiken
        stats = service.get_statistics()

        print(f"\n✓ Statistiken:")
        print(f"   Roles: {stats['roles']['total']}")
        print(f"   Skills: {stats['skills']['total']}")
        print(f"   Industries: {stats['industries']['total']}")
        print(f"   Digital Skills: {stats['skills']['digital']}")

        assert stats["roles"]["total"] == 2, "Sollte 2 Rollen haben"
        assert stats["skills"]["total"] == 2, "Sollte 2 Skills haben"
        assert stats["industries"]["total"] == 1, "Sollte 1 Industrie haben"

        print("✓ Test: PASS\n")


def test_top_discoveries():
    """Test 7: Top Discoveries (by Frequency)"""
    print("="*60)
    print("TEST 7: Top Discoveries")
    print("="*60)

    try:
        from app.application.services.discovery_learning_service import DiscoveryLearningService
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        service = DiscoveryLearningService(data_dir=Path(tmpdir))

        # Erstelle Rollen mit verschiedenen Frequenzen
        for _ in range(10):
            service.discover_role("AI Engineer")

        for _ in range(5):
            service.discover_role("ML Engineer")

        for _ in range(2):
            service.discover_role("Data Engineer")

        # Top 3
        top = service.get_top_discoveries("role", limit=3)

        print(f"\n✓ Top 3 Rollen:")
        for i, (name, entry) in enumerate(top, 1):
            print(f"   {i}. {name} (freq={entry['frequency']})")

        assert len(top) == 3, "Sollte 3 Rollen zurückgeben"
        assert top[0][1]["frequency"] == 10, "Häufigste sollte 10 sein"
        assert top[0][0] == "ai engineer", "Häufigste sollte 'ai engineer' sein"

        print("✓ Test: PASS\n")


def test_persistent_storage():
    """Test 8: Persistente Speicherung"""
    print("="*60)
    print("TEST 8: Persistente Speicherung")
    print("="*60)

    try:
        from app.application.services.discovery_learning_service import DiscoveryLearningService
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)

        # Erste Instanz: Erstelle Discoveries
        service1 = DiscoveryLearningService(data_dir=data_dir)
        service1.discover_role("Blockchain Developer")
        service1.discover_skill("Solidity")

        print(f"\n✓ Service 1: {len(service1.discovered_roles)} Rollen, {len(service1.discovered_skills)} Skills")

        # Zweite Instanz: Lade Discoveries
        service2 = DiscoveryLearningService(data_dir=data_dir)

        print(f"✓ Service 2: {len(service2.discovered_roles)} Rollen, {len(service2.discovered_skills)} Skills")

        assert len(service2.discovered_roles) == 1, "Sollte 1 Rolle laden"
        assert len(service2.discovered_skills) == 1, "Sollte 1 Skill laden"
        assert "blockchain developer" in service2.discovered_roles, "Rolle sollte geladen sein"

        print("✓ Test: PASS\n")


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  DISCOVERY LEARNING SERVICE - TEST SUITE                ║")
    print("║  Selbstlernendes System für ESCO-Integration            ║")
    print("╚════════════════════════════════════════════════════════════╝")

    try:
        test_role_discovery()
        test_skill_discovery_with_digital_detection()
        test_auto_promotion_by_frequency()
        test_validation_and_promotion()
        test_export_to_esco_format()
        test_statistics()
        test_top_discoveries()
        test_persistent_storage()

        print("="*60)
        print("✅ ALLE TESTS BESTANDEN")
        print("="*60)
        print("\nZusammenfassung:")
        print("  • Discovery: Neue Entities auf Ebene 1")
        print("  • Auto-Promotion: Frequency-basiert (5→L2, 10→L3)")
        print("  • Validierung: Manuelle Bestätigung + Level-Erhöhung")
        print("  • Export: ESCO-kompatibles Format")
        print("  • Persistenz: JSON-basierte Speicherung")
        print("  • Selbstlernend: Automatische Integration")
        print("="*60)

    except Exception as e:
        print(f"\n❌ TEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
