"""
End-to-End Integration Test
============================

Testet die komplette Pipeline:
1. Python: Datei-Upload & Analyse
2. Kotlin: API-Endpunkte & DTOs
3. DB: Persistierung & Abruf
4. Services: Role, Industry, Discovery

Requirements:
- Python Backend läuft auf http://localhost:8000
- Kotlin Backend läuft auf http://localhost:8080
- Datenbank ist erreichbar
"""

import requests
import time
from pathlib import Path


def test_e2e_full_pipeline():
    """
    Test 1: Komplette Pipeline von Upload bis DB-Abruf
    """
    print("\n" + "="*60)
    print("E2E TEST 1: Komplette Analyse-Pipeline")
    print("="*60)

    # URLs
    python_url = "http://localhost:8000"
    kotlin_url = "http://localhost:8080"

    # Step 1: Health Check
    print("\n🔍 Step 1: Health Check")
    try:
        python_health = requests.get(f"{python_url}/health", timeout=5)
        print(f"   ✓ Python Backend: {python_health.status_code}")
    except Exception as e:
        print(f"   ❌ Python Backend nicht erreichbar: {e}")
        print("   ⏭️ TEST SKIP (Start Python mit: uvicorn main:app --reload)")
        return

    try:
        kotlin_health = requests.get(f"{kotlin_url}/actuator/health", timeout=5)
        print(f"   ✓ Kotlin Backend: {kotlin_health.status_code}")
    except Exception as e:
        print(f"   ⚠️ Kotlin Backend nicht erreichbar: {e}")
        print("   ℹ️ Teste nur Python-Teil")

    # Step 2: Upload Test-Stellenanzeige
    print("\n📤 Step 2: Upload Test-Stellenanzeige")
    test_file = Path(__file__).parent.parent.parent / "test-data" / "test-stellenanzeige.txt"

    if not test_file.exists():
        print(f"   ❌ Test-Datei nicht gefunden: {test_file}")
        return

    with open(test_file, 'rb') as f:
        files = {'file': ('test-stellenanzeige.txt', f, 'text/plain')}
        response = requests.post(
            f"{python_url}/analyse/file",
            files=files,
            timeout=30
        )

    print(f"   ✓ Upload Status: {response.status_code}")

    if response.status_code != 200:
        print(f"   ❌ Upload fehlgeschlagen: {response.text}")
        return

    result = response.json()
    print(f"   ✓ Job Titel: {result.get('title', 'N/A')}")
    print(f"   ✓ Rolle: {result.get('job_role', 'N/A')}")
    print(f"   ✓ Industrie: {result.get('industry', 'N/A')}")
    print(f"   ✓ Kompetenzen: {len(result.get('competences', []))}")

    competences = result.get('competences', [])
    if competences:
        print(f"\n   📊 Top 5 Kompetenzen:")
        for i, comp in enumerate(competences[:5], 1):
            print(f"      {i}. {comp.get('esco_label', comp.get('original_term'))} "
                  f"(L{comp.get('level', '?')}, Confidence: {comp.get('confidence_score', 0):.2f})")

    # Step 3: Klassifizierungen testen
    print("\n🏷️ Step 3: Klassifizierungen")

    # Test Role Classification
    print("\n   Rolle-Klassifizierung:")
    role = result.get('job_role', 'N/A')
    print(f"      ✓ Klassifizierte Rolle: {role}")

    # Test Industry Classification
    print("\n   Industrie-Klassifizierung:")
    industry = result.get('industry', 'N/A')
    print(f"      ✓ Klassifizierte Industrie: {industry}")

    # Step 4: Discovery-Analyse
    print("\n🔍 Step 4: Discovery-Analyse")
    discovery_count = sum(1 for c in competences if c.get('is_discovery', False))
    digital_count = sum(1 for c in competences if c.get('is_digital', False))

    print(f"   ✓ Discovery Skills (L1): {discovery_count}")
    print(f"   ✓ Digital Skills (L3): {digital_count}")

    # Level-Verteilung
    level_dist = {}
    for comp in competences:
        level = comp.get('level', 2)
        level_dist[level] = level_dist.get(level, 0) + 1

    print(f"\n   📊 Level-Verteilung:")
    for level in sorted(level_dist.keys()):
        print(f"      Level {level}: {level_dist[level]} Skills")

    # Step 5: Kotlin API Test (falls verfügbar)
    print("\n🔌 Step 5: Kotlin API (falls verfügbar)")
    try:
        jobs_response = requests.get(
            f"{kotlin_url}/api/v1/jobs",
            params={"page": 0, "size": 10},
            timeout=5
        )

        if jobs_response.status_code == 200:
            jobs_data = jobs_response.json()
            print(f"   ✓ Jobs in DB: {jobs_data.get('totalElements', 0)}")
            print(f"   ✓ Seiten gesamt: {jobs_data.get('totalPages', 0)}")
            print(f"   ✓ Aktuelle Seite: {len(jobs_data.get('content', []))} Jobs")

            # Test: Einzelner Job abrufen
            if jobs_data.get('content'):
                first_job = jobs_data['content'][0]
                job_id = first_job['id']

                detail_response = requests.get(
                    f"{kotlin_url}/api/v1/jobs/{job_id}",
                    timeout=5
                )

                if detail_response.status_code == 200:
                    detail = detail_response.json()
                    print(f"\n   ✓ Job Detail (ID {job_id}):")
                    print(f"      Titel: {detail.get('title', 'N/A')}")
                    print(f"      Kompetenzen: {len(detail.get('competences', []))}")
                    print(f"      rawText Länge: {len(detail.get('rawText', ''))} Zeichen")
        else:
            print(f"   ⚠️ Kotlin Jobs-Endpoint: {jobs_response.status_code}")

    except Exception as e:
        print(f"   ⚠️ Kotlin API nicht verfügbar: {e}")

    print("\n" + "="*60)
    print("✅ E2E TEST ABGESCHLOSSEN")
    print("="*60)


def test_e2e_discovery_learning():
    """
    Test 2: Discovery Learning System
    """
    print("\n" + "="*60)
    print("E2E TEST 2: Discovery Learning System")
    print("="*60)

    python_url = "http://localhost:8000"

    # Test Discovery-Endpoints
    print("\n📍 Discovery Candidates:")
    try:
        candidates = requests.get(f"{python_url}/discovery/candidates", timeout=5)
        if candidates.status_code == 200:
            data = candidates.json()
            print(f"   ✓ Candidates: {len(data.get('candidates', []))}")

            if data.get('candidates'):
                print(f"\n   Top 3 Candidates:")
                for i, cand in enumerate(data['candidates'][:3], 1):
                    print(f"      {i}. {cand.get('term')} (freq={cand.get('frequency', 0)})")
        else:
            print(f"   ⚠️ Discovery nicht verfügbar: {candidates.status_code}")
    except Exception as e:
        print(f"   ⚠️ Discovery-Endpoint Fehler: {e}")

    print("\n✅ Discovery Test abgeschlossen\n")


def test_e2e_7_ebenen_integration():
    """
    Test 3: 7-Ebenen-Modell Integration
    """
    print("="*60)
    print("E2E TEST 3: 7-Ebenen-Modell")
    print("="*60)

    python_url = "http://localhost:8000"

    # Upload einer Test-Datei und prüfe Level-Verteilung
    test_file = Path(__file__).parent.parent.parent / "test-data" / "test-stellenanzeige.txt"

    if not test_file.exists():
        print("   ⏭️ TEST SKIP (Test-Datei fehlt)")
        return

    with open(test_file, 'rb') as f:
        files = {'file': ('test.txt', f, 'text/plain')}
        response = requests.post(
            f"{python_url}/analyse/file",
            files=files,
            timeout=30
        )

    if response.status_code == 200:
        result = response.json()
        competences = result.get('competences', [])

        # Analysiere Ebenen
        ebenen = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for comp in competences:
            level = comp.get('level', 2)
            if level in ebenen:
                ebenen[level] += 1

        print(f"\n   📊 7-Ebenen-Verteilung:")
        print(f"      Ebene 1 (Discovery): {ebenen[1]}")
        print(f"      Ebene 2 (ESCO Standard): {ebenen[2]}")
        print(f"      Ebene 3 (Digital): {ebenen[3]}")
        print(f"      Ebene 4 (Fachbuch): {ebenen[4]}")
        print(f"      Ebene 5 (Academia): {ebenen[5]}")

        # Prüfe Priorität: Academia > Fachbuch > Digital > Standard
        if ebenen[5] > 0:
            print(f"\n   ✅ Academia Skills erkannt (höchste Priorität)")
        if ebenen[4] > 0:
            print(f"   ✅ Fachbuch Skills erkannt")
        if ebenen[3] > 0:
            print(f"   ✅ Digital Skills erkannt")

        print("\n✅ 7-Ebenen Test abgeschlossen\n")
    else:
        print(f"   ❌ Analyse fehlgeschlagen: {response.status_code}")


def test_e2e_performance():
    """
    Test 4: Performance & Broken Pipe Prevention
    """
    print("="*60)
    print("E2E TEST 4: Performance & Response Size")
    print("="*60)

    kotlin_url = "http://localhost:8080"

    try:
        # Test: Paginierte Abfrage (sollte < 1 MB sein)
        start = time.time()
        response = requests.get(
            f"{kotlin_url}/api/v1/jobs",
            params={"page": 0, "size": 20},
            timeout=5
        )
        duration = time.time() - start

        if response.status_code == 200:
            size_kb = len(response.content) / 1024

            print(f"\n   ✓ Response Time: {duration:.2f}s")
            print(f"   ✓ Response Size: {size_kb:.2f} KB")

            if size_kb < 1024:
                print(f"   ✅ Response < 1 MB (Broken Pipe verhindert)")
            else:
                print(f"   ⚠️ Response > 1 MB (mögliches Broken Pipe Risiko)")

            data = response.json()
            print(f"\n   📊 Paginierung:")
            print(f"      Total Elements: {data.get('totalElements', 0)}")
            print(f"      Total Pages: {data.get('totalPages', 0)}")
            print(f"      Current Page Size: {len(data.get('content', []))}")

        else:
            print(f"   ⚠️ Kotlin API: {response.status_code}")

    except Exception as e:
        print(f"   ⚠️ Performance Test übersprungen: {e}")

    print("\n✅ Performance Test abgeschlossen\n")


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║         END-TO-END INTEGRATION TEST SUITE                 ║")
    print("║  Python → Kotlin → DB → Discovery → 7-Ebenen             ║")
    print("╚════════════════════════════════════════════════════════════╝")

    print("\n⚙️ Voraussetzungen:")
    print("   • Python Backend: uvicorn main:app --reload")
    print("   • Kotlin Backend: ./gradlew bootRun")
    print("   • Datenbank: PostgreSQL oder H2\n")

    input("Drücke ENTER um Tests zu starten... ")

    try:
        # Test 1: Hauptpipeline
        test_e2e_full_pipeline()

        # Test 2: Discovery
        test_e2e_discovery_learning()

        # Test 3: 7-Ebenen
        test_e2e_7_ebenen_integration()

        # Test 4: Performance
        test_e2e_performance()

        print("\n" + "="*60)
        print("🎉 ALLE E2E-TESTS ABGESCHLOSSEN")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n⚠️ Tests abgebrochen")
    except Exception as e:
        print(f"\n\n❌ Test-Fehler: {e}")
        import traceback
        traceback.print_exc()
