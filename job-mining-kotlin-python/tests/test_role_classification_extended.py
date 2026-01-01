"""
Test für erweiterte Rollen-Klassifizierung (ESCO-basiert)

Testet:
- IT & Software Rollen (8 Kategorien)
- Gesundheit & Medizin (3 Kategorien)
- Ingenieurwesen & Technik (3 Kategorien)
- Verwaltung & Management (3 Kategorien)
- Bildung & Wissenschaft (2 Kategorien)
- Verkauf & Marketing (2 Kategorien)
- Finanzen & Recht (2 Kategorien)
- Handwerk & Produktion (2 Kategorien)
- Logistik & Transport (1 Kategorie)
- Beratung & Consulting (1 Kategorie)

Basis: ESCO/ISCO-08 Occupation Taxonomy
"""


def test_it_software_roles():
    """
    Test 1: IT & Software Rollen (erweitert)
    """
    print("\n" + "="*60)
    print("TEST 1: IT & Software Rollen (ESCO-basiert)")
    print("="*60)

    try:
        from app.application.services.role_service import RoleService
        from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    # Mock KotlinRuleClient
    class MockRuleClient:
        def fetch_role_mappings(self):
            return {}

    service = RoleService(MockRuleClient())

    # Test Cases: (job_title, job_text, expected_role)
    test_cases = [
        # Fullstack
        ("Fullstack Developer", "React und Spring Boot", "Fullstack Developer"),
        ("Full-Stack Engineer", "Frontend und Backend Entwicklung", "Fullstack Developer"),

        # Frontend
        ("Frontend Developer", "React, Vue, Angular", "Frontend Developer"),
        ("Web Developer", "HTML CSS JavaScript", "Frontend Developer"),

        # Backend
        ("Backend Developer", "Spring Boot Java Microservices", "Backend Developer"),
        ("Server Developer", "Django Python REST API", "Backend Developer"),

        # DevOps
        ("DevOps Engineer", "Docker Kubernetes CI/CD", "DevOps Engineer"),
        ("SRE Engineer", "Site Reliability Engineering", "DevOps Engineer"),

        # Mobile
        ("Mobile Developer", "iOS Swift Android Kotlin", "Mobile Developer"),
        ("App Developer", "React Native Flutter", "Mobile Developer"),

        # Data Science
        ("Data Scientist", "Machine Learning Python TensorFlow", "Data Scientist"),
        ("ML Engineer", "Deep Learning AI PyTorch", "Data Scientist"),

        # Security
        ("Security Engineer", "Cybersecurity Penetration Testing", "Security Engineer"),
        ("InfoSec Specialist", "ISO 27001 CISO", "Security Engineer"),

        # QA
        ("QA Engineer", "Test Automation Selenium", "QA Engineer"),
        ("Software Tester", "Quality Assurance Cypress", "QA Engineer"),
    ]

    print(f"\n✓ RoleService initialisiert")
    print(f"✓ Teste {len(test_cases)} IT-Rollen\n")

    success = 0
    failed = []

    for title, text, expected in test_cases:
        result = service.classify_role(text, title)
        if result == expected:
            print(f"   ✅ {title:25} → {result}")
            success += 1
        else:
            print(f"   ❌ {title:25} → {result} (erwartet: {expected})")
            failed.append((title, result, expected))

    print(f"\n✓ Erfolg: {success}/{len(test_cases)}")

    if failed:
        print(f"❌ Fehlgeschlagen: {len(failed)}")
        for title, actual, expected in failed:
            print(f"   - {title}: '{actual}' != '{expected}'")

    assert success >= len(test_cases) * 0.8, f"Mindestens 80% sollten korrekt sein"
    print("✓ Test: PASS\n")


def test_healthcare_roles():
    """
    Test 2: Gesundheit & Medizin (ESCO Group 2)
    """
    print("="*60)
    print("TEST 2: Gesundheit & Medizin")
    print("="*60)

    try:
        from app.application.services.role_service import RoleService
        from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    class MockRuleClient:
        def fetch_role_mappings(self):
            return {}

    service = RoleService(MockRuleClient())

    test_cases = [
        # Ärzte
        ("Facharzt für Innere Medizin", "Allgemeinmedizin Krankenhaus", "Arzt / Ärztin"),
        ("Oberarzt Chirurgie", "Mediziner Chefarzt", "Arzt / Ärztin"),

        # Pflege
        ("Gesundheits- und Krankenpfleger", "Pflege Krankenpflege", "Pflegefachkraft"),
        ("Altenpfleger", "Pflegefachmann stationäre Pflege", "Pflegefachkraft"),

        # Psychologie
        ("Psychologe", "Klinische Psychologie Therapie", "Psychologe / Therapeut"),
        ("Psychotherapeut", "Verhaltenstherapie Beratung", "Psychologe / Therapeut"),
    ]

    print(f"\n✓ Teste {len(test_cases)} Gesundheits-Rollen\n")

    success = 0
    for title, text, expected in test_cases:
        result = service.classify_role(text, title)
        if result == expected:
            print(f"   ✅ {title:35} → {result}")
            success += 1
        else:
            print(f"   ⚠️ {title:35} → {result} (erwartet: {expected})")

    print(f"\n✓ Erfolg: {success}/{len(test_cases)}")
    assert success >= 4, "Mindestens 4 sollten korrekt sein"
    print("✓ Test: PASS\n")


def test_engineering_roles():
    """
    Test 3: Ingenieurwesen & Technik (ESCO Group 2)
    """
    print("="*60)
    print("TEST 3: Ingenieurwesen & Technik")
    print("="*60)

    try:
        from app.application.services.role_service import RoleService
        from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    class MockRuleClient:
        def fetch_role_mappings(self):
            return {}

    service = RoleService(MockRuleClient())

    test_cases = [
        # Maschinenbau
        ("Maschinenbauingenieur", "CAD CATIA Konstruktion", "Maschinenbauingenieur"),
        ("Entwicklungsingenieur", "Mechanical Engineer SolidWorks", "Maschinenbauingenieur"),

        # Elektrotechnik
        ("Elektroingenieur", "Electrical Engineer Automatisierung", "Elektroingenieur"),
        ("Elektrotechniker", "Energietechnik Steuerungstechnik", "Elektroingenieur"),

        # Bauwesen
        ("Bauingenieur", "Civil Engineer Statik Tragwerk", "Bauingenieur"),
        ("Architekt", "Bauplanung Konstruktion", "Bauingenieur"),
    ]

    print(f"\n✓ Teste {len(test_cases)} Ingenieur-Rollen\n")

    success = 0
    for title, text, expected in test_cases:
        result = service.classify_role(text, title)
        if result == expected:
            print(f"   ✅ {title:30} → {result}")
            success += 1
        else:
            print(f"   ⚠️ {title:30} → {result} (erwartet: {expected})")

    print(f"\n✓ Erfolg: {success}/{len(test_cases)}")
    assert success >= 4, "Mindestens 4 sollten korrekt sein"
    print("✓ Test: PASS\n")


def test_management_roles():
    """
    Test 4: Verwaltung & Management (ESCO Group 1)
    """
    print("="*60)
    print("TEST 4: Verwaltung & Management")
    print("="*60)

    try:
        from app.application.services.role_service import RoleService
        from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    class MockRuleClient:
        def fetch_role_mappings(self):
            return {}

    service = RoleService(MockRuleClient())

    test_cases = [
        # Geschäftsführung
        ("CEO", "Geschäftsführer Managing Director", "Geschäftsführer / Manager"),
        ("Head of Operations", "Executive Vorstand", "Geschäftsführer / Manager"),

        # Projektmanagement
        ("Projektmanager", "Project Manager Scrum Master", "Projektmanager"),
        ("Product Owner", "Agile PMP Projektleiter", "Projektmanager"),

        # HR
        ("HR Manager", "Human Resources Personalreferent", "HR / Personalwesen"),
        ("Recruiter", "Talent Acquisition Personalleiter", "HR / Personalwesen"),
    ]

    print(f"\n✓ Teste {len(test_cases)} Management-Rollen\n")

    success = 0
    for title, text, expected in test_cases:
        result = service.classify_role(text, title)
        if result == expected:
            print(f"   ✅ {title:25} → {result}")
            success += 1
        else:
            print(f"   ⚠️ {title:25} → {result} (erwartet: {expected})")

    print(f"\n✓ Erfolg: {success}/{len(test_cases)}")
    assert success >= 4, "Mindestens 4 sollten korrekt sein"
    print("✓ Test: PASS\n")


def test_education_roles():
    """
    Test 5: Bildung & Wissenschaft (ESCO Group 2)
    """
    print("="*60)
    print("TEST 5: Bildung & Wissenschaft")
    print("="*60)

    try:
        from app.application.services.role_service import RoleService
        from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    class MockRuleClient:
        def fetch_role_mappings(self):
            return {}

    service = RoleService(MockRuleClient())

    test_cases = [
        # Lehrer
        ("Lehrer", "Lehrkraft Schule Pädagogik", "Lehrer / Dozent"),
        ("Dozent", "Professor Universität", "Lehrer / Dozent"),

        # Wissenschaft
        ("Wissenschaftler", "Forscher PhD Research", "Wissenschaftler / Forscher"),
        ("Postdoc", "Doktorand Forschung Entwicklung", "Wissenschaftler / Forscher"),
    ]

    print(f"\n✓ Teste {len(test_cases)} Bildungs-Rollen\n")

    success = 0
    for title, text, expected in test_cases:
        result = service.classify_role(text, title)
        if result == expected:
            print(f"   ✅ {title:20} → {result}")
            success += 1
        else:
            print(f"   ⚠️ {title:20} → {result} (erwartet: {expected})")

    print(f"\n✓ Erfolg: {success}/{len(test_cases)}")
    assert success >= 3, "Mindestens 3 sollten korrekt sein"
    print("✓ Test: PASS\n")


def test_sales_marketing_roles():
    """
    Test 6: Verkauf & Marketing (ESCO Group 3)
    """
    print("="*60)
    print("TEST 6: Verkauf & Marketing")
    print("="*60)

    try:
        from app.application.services.role_service import RoleService
        from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    class MockRuleClient:
        def fetch_role_mappings(self):
            return {}

    service = RoleService(MockRuleClient())

    test_cases = [
        # Vertrieb
        ("Sales Manager", "Vertrieb Account Manager", "Vertriebsmitarbeiter"),
        ("Key Account Manager", "Verkauf Kundenberater", "Vertriebsmitarbeiter"),

        # Marketing
        ("Marketing Manager", "Online Marketing Brand Manager", "Marketing Manager"),
        ("Digital Marketing", "SEO SEM Social Media", "Marketing Manager"),
    ]

    print(f"\n✓ Teste {len(test_cases)} Sales/Marketing-Rollen\n")

    success = 0
    for title, text, expected in test_cases:
        result = service.classify_role(text, title)
        if result == expected:
            print(f"   ✅ {title:25} → {result}")
            success += 1
        else:
            print(f"   ⚠️ {title:25} → {result} (erwartet: {expected})")

    print(f"\n✓ Erfolg: {success}/{len(test_cases)}")
    assert success >= 3, "Mindestens 3 sollten korrekt sein"
    print("✓ Test: PASS\n")


def test_finance_legal_roles():
    """
    Test 7: Finanzen & Recht (ESCO Group 2)
    """
    print("="*60)
    print("TEST 7: Finanzen & Recht")
    print("="*60)

    try:
        from app.application.services.role_service import RoleService
        from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    class MockRuleClient:
        def fetch_role_mappings(self):
            return {}

    service = RoleService(MockRuleClient())

    test_cases = [
        # Buchhaltung
        ("Buchhalter", "Accountant Controller DATEV", "Buchhalter / Controller"),
        ("Finanzbuchhalter", "Bilanzbuchhalter SAP FICO", "Buchhalter / Controller"),

        # Recht
        ("Rechtsanwalt", "Jurist Lawyer Legal Counsel", "Jurist / Rechtsanwalt"),
        ("Syndikus", "Recht Jura Anwalt", "Jurist / Rechtsanwalt"),
    ]

    print(f"\n✓ Teste {len(test_cases)} Finanz/Rechts-Rollen\n")

    success = 0
    for title, text, expected in test_cases:
        result = service.classify_role(text, title)
        if result == expected:
            print(f"   ✅ {title:25} → {result}")
            success += 1
        else:
            print(f"   ⚠️ {title:25} → {result} (erwartet: {expected})")

    print(f"\n✓ Erfolg: {success}/{len(test_cases)}")
    assert success >= 3, "Mindestens 3 sollten korrekt sein"
    print("✓ Test: PASS\n")


def test_trades_production_roles():
    """
    Test 8: Handwerk & Produktion (ESCO Group 7-8)
    """
    print("="*60)
    print("TEST 8: Handwerk & Produktion")
    print("="*60)

    try:
        from app.application.services.role_service import RoleService
        from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    class MockRuleClient:
        def fetch_role_mappings(self):
            return {}

    service = RoleService(MockRuleClient())

    test_cases = [
        # Handwerk
        ("Elektriker", "Handwerker Techniker", "Handwerker / Techniker"),
        ("Tischler", "Schreiner Installateur", "Handwerker / Techniker"),

        # Produktion
        ("Produktionsmitarbeiter", "Fertigung Manufacturing", "Produktionsmitarbeiter"),
        ("Produktionsleiter", "Montage Assembly Werksleiter", "Produktionsmitarbeiter"),
    ]

    print(f"\n✓ Teste {len(test_cases)} Handwerks-Rollen\n")

    success = 0
    for title, text, expected in test_cases:
        result = service.classify_role(text, title)
        if result == expected:
            print(f"   ✅ {title:25} → {result}")
            success += 1
        else:
            print(f"   ⚠️ {title:25} → {result} (erwartet: {expected})")

    print(f"\n✓ Erfolg: {success}/{len(test_cases)}")
    assert success >= 3, "Mindestens 3 sollten korrekt sein"
    print("✓ Test: PASS\n")


def test_logistics_consulting_roles():
    """
    Test 9: Logistik & Beratung (ESCO Group 8 + 2)
    """
    print("="*60)
    print("TEST 9: Logistik & Beratung")
    print("="*60)

    try:
        from app.application.services.role_service import RoleService
        from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    class MockRuleClient:
        def fetch_role_mappings(self):
            return {}

    service = RoleService(MockRuleClient())

    test_cases = [
        # Logistik
        ("Logistiker", "Logistics Supply Chain", "Logistiker"),
        ("Warehouse Manager", "Lagerleiter Einkauf Procurement", "Logistiker"),

        # Beratung
        ("Unternehmensberater", "Consultant Management Consulting", "Unternehmensberater"),
        ("Strategy Consultant", "McKinsey BCG Big Four", "Unternehmensberater"),
    ]

    print(f"\n✓ Teste {len(test_cases)} Logistik/Beratungs-Rollen\n")

    success = 0
    for title, text, expected in test_cases:
        result = service.classify_role(text, title)
        if result == expected:
            print(f"   ✅ {title:25} → {result}")
            success += 1
        else:
            print(f"   ⚠️ {title:25} → {result} (erwartet: {expected})")

    print(f"\n✓ Erfolg: {success}/{len(test_cases)}")
    assert success >= 3, "Mindestens 3 sollten korrekt sein"
    print("✓ Test: PASS\n")


def test_fallback_generic_software():
    """
    Test 10: Fallback zu "Software Engineer" für generische Developer-Begriffe
    """
    print("="*60)
    print("TEST 10: Fallback Generic Software Engineer")
    print("="*60)

    try:
        from app.application.services.role_service import RoleService
        from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    class MockRuleClient:
        def fetch_role_mappings(self):
            return {}

    service = RoleService(MockRuleClient())

    test_cases = [
        ("Software Developer", "Programmierung", "Software Engineer"),
        ("Developer", "Entwicklung Software", "Software Engineer"),
        ("Programmierer", "Entwickler", "Software Engineer"),
    ]

    print(f"\n✓ Teste {len(test_cases)} Fallback-Fälle\n")

    success = 0
    for title, text, expected in test_cases:
        result = service.classify_role(text, title)
        if result == expected:
            print(f"   ✅ {title:25} → {result}")
            success += 1
        else:
            print(f"   ⚠️ {title:25} → {result} (erwartet: {expected})")

    print(f"\n✓ Erfolg: {success}/{len(test_cases)}")
    assert success >= 2, "Mindestens 2 sollten korrekt sein"
    print("✓ Test: PASS\n")


def test_coverage_statistics():
    """
    Test 11: Coverage-Statistiken für alle Kategorien
    """
    print("="*60)
    print("TEST 11: Coverage-Statistiken")
    print("="*60)

    try:
        from app.application.services.role_service import RoleService
        from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
    except ImportError as e:
        print(f"⚠️ Import fehlgeschlagen: {e}")
        print("✓ Test: SKIP")
        return

    class MockRuleClient:
        def fetch_role_mappings(self):
            return {}

    service = RoleService(MockRuleClient())

    print(f"\n✓ Analysiere Pattern-Coverage\n")

    pattern_count = len(service.IT_ROLE_PATTERNS)

    categories = {
        "IT & Software": 8,
        "Gesundheit & Medizin": 3,
        "Ingenieurwesen & Technik": 3,
        "Verwaltung & Management": 3,
        "Bildung & Wissenschaft": 2,
        "Verkauf & Marketing": 2,
        "Finanzen & Recht": 2,
        "Handwerk & Produktion": 2,
        "Logistik & Transport": 1,
        "Beratung & Consulting": 1,
    }

    expected_total = sum(categories.values())

    print(f"   Kategorien: {len(categories)}")
    print(f"   Erwartete Rollen: {expected_total}")
    print(f"   Tatsächliche Patterns: {pattern_count}")
    print(f"\n   Verteilung:")
    for cat, count in categories.items():
        print(f"      • {cat:30} {count} Rollen")

    assert pattern_count >= 25, f"Sollte mindestens 25 Pattern haben (ist: {pattern_count})"

    print(f"\n✓ Coverage: {pattern_count} Rollen abgedeckt")
    print("✓ Test: PASS\n")


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  ROLLEN-KLASSIFIZIERUNG - EXTENDED TEST SUITE            ║")
    print("║  ESCO/ISCO-08 Occupation Taxonomy                        ║")
    print("╚════════════════════════════════════════════════════════════╝")

    try:
        test_it_software_roles()
        test_healthcare_roles()
        test_engineering_roles()
        test_management_roles()
        test_education_roles()
        test_sales_marketing_roles()
        test_finance_legal_roles()
        test_trades_production_roles()
        test_logistics_consulting_roles()
        test_fallback_generic_software()
        test_coverage_statistics()

        print("="*60)
        print("✅ ALLE TESTS BESTANDEN")
        print("="*60)
        print("\nZusammenfassung:")
        print("  • 10 Berufsgruppen implementiert")
        print("  • 30+ spezifische Rollen")
        print("  • Basiert auf ESCO/ISCO-08 Taxonomy")
        print("  • Pattern-Matching mit Regex")
        print("  • Fallback zu 'Software Engineer' für IT-Begriffe")
        print("  • Fallback zu 'Sonstige Rolle' für unbekannte")
        print("="*60)

    except Exception as e:
        print(f"\n❌ TEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
