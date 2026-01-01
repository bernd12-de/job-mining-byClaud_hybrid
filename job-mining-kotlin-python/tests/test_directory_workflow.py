"""
Test für Directory Workflow Manager (Prio 3)

Testet:
- Directory-Struktur Erstellung
- add_job() Funktionalität
- run_workflow() Execution
- Archivierung (YYYY-MM)
"""

import tempfile
import shutil
from pathlib import Path


def test_directory_setup():
    """
    Test 1: Directory-Struktur wird korrekt erstellt
    """
    from app.application.directory_workflow_manager import DirectoryWorkflowManager

    print("\n" + "=" * 60)
    print("TEST 1: Directory-Struktur")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp_dir:
        manager = DirectoryWorkflowManager(base_dir=tmp_dir)

        # Prüfe Verzeichnisse
        assert manager.incoming.exists()
        assert manager.processing.exists()
        assert manager.archive.exists()
        assert manager.results.exists()
        assert manager.reports.exists()

        print("✓ Alle Verzeichnisse erstellt")
        print("✓ Test: PASS")


def test_add_job():
    """
    Test 2: add_job() funktioniert
    """
    from app.application.directory_workflow_manager import DirectoryWorkflowManager

    print("\n" + "=" * 60)
    print("TEST 2: add_job() Funktionalität")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp_dir:
        manager = DirectoryWorkflowManager(base_dir=tmp_dir)

        # Erstelle Test-Datei
        test_file = Path(tmp_dir) / "test_job.pdf"
        test_file.write_text("Test PDF Content")

        # Add Job
        new_name = manager.add_job(
            str(test_file),
            metadata={'company': 'Test GmbH', 'position': 'Developer'}
        )

        print(f"✓ Original: test_job.pdf")
        print(f"✓ Neuer Name: {new_name}")

        # Prüfe ob Datei in incoming/
        incoming_file = manager.incoming / new_name
        assert incoming_file.exists()

        # Prüfe Metadata
        meta_file = incoming_file.with_suffix(incoming_file.suffix + '.meta.json')
        assert meta_file.exists()

        print("✓ Datei in incoming/")
        print("✓ Metadata gespeichert")
        print("✓ Test: PASS")


def test_workflow_execution():
    """
    Test 3: run_workflow() verarbeitet Dateien
    """
    from app.application.directory_workflow_manager import DirectoryWorkflowManager

    print("\n" + "=" * 60)
    print("TEST 3: Workflow Execution")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp_dir:
        manager = DirectoryWorkflowManager(base_dir=tmp_dir)

        # Erstelle 2 Test-Jobs
        for i in range(2):
            test_file = Path(tmp_dir) / f"job_{i}.pdf"
            test_file.write_text(f"Job {i} Content")
            manager.add_job(str(test_file), metadata={'company': f'Company {i}'})

        # Run Workflow
        results = manager.run_workflow()

        print(f"✓ Verarbeitete Dateien: {len(results)}")
        assert len(results) == 2

        # Prüfe ob archiviert
        arch_files = list(manager.archive.rglob("*.pdf"))
        print(f"✓ Archivierte Dateien: {len(arch_files)}")
        assert len(arch_files) == 2

        # Prüfe ob Results existieren
        json_files = list(manager.results.glob("*.json"))
        csv_files = list(manager.results.glob("*.csv"))
        print(f"✓ JSON Results: {len(json_files)}")
        print(f"✓ CSV Results: {len(csv_files)}")
        assert len(json_files) >= 1
        assert len(csv_files) >= 1

        # Prüfe ob Reports existieren
        html_files = list(manager.reports.glob("*.html"))
        print(f"✓ HTML Reports: {len(html_files)}")
        assert len(html_files) >= 1

        print("✓ Test: PASS")


def test_monthly_archiving():
    """
    Test 4: Archivierung nach Monat (YYYY-MM)
    """
    from app.application.directory_workflow_manager import DirectoryWorkflowManager
    from datetime import datetime

    print("\n" + "=" * 60)
    print("TEST 4: Monatliche Archivierung")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp_dir:
        manager = DirectoryWorkflowManager(base_dir=tmp_dir)

        # Add Job
        test_file = Path(tmp_dir) / "test.pdf"
        test_file.write_text("Test")
        manager.add_job(str(test_file))

        # Run
        manager.run_workflow()

        # Prüfe Monat-Ordner
        month = datetime.now().strftime("%Y-%m")
        month_dir = manager.archive / month

        print(f"✓ Monat: {month}")
        assert month_dir.exists()

        files_in_month = list(month_dir.glob("*.pdf"))
        print(f"✓ Dateien in {month}: {len(files_in_month)}")
        assert len(files_in_month) == 1

        print("✓ Test: PASS")


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  DIRECTORY WORKFLOW MANAGER - TEST SUITE                  ║")
    print("╚════════════════════════════════════════════════════════════╝")

    try:
        test_directory_setup()
        test_add_job()
        test_workflow_execution()
        test_monthly_archiving()

        print("\n" + "=" * 60)
        print("✅ ALLE TESTS BESTANDEN")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
