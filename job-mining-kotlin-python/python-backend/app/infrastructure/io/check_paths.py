import os
from pathlib import Path

def check_system():
    # 1. Projekt-Struktur ermitteln
    root = Path(__file__).parent.absolute()
    python_data = root / "python-backend" / "data" / "esco"
    kotlin_data = root / "kotlin-api" / "src" / "main" / "resources" # Falls dort etwas liegt
    shared_data = root / "data" / "esco"

    print(f"🔍 Projekt-Root: {root}")
    print("-" * 50)

    # 2. ESCO-Dateien suchen
    targets = {
        "Shared Data (Docker Volume)": shared_data,
        "Python Local Data": python_data,
    }

    found_any = False
    for name, path in targets.items():
        if path.exists():
            files = list(path.glob("*.csv"))
            print(f"✅ {name}: GEFUNDEN")
            print(f"   -> Pfad: {path}")
            print(f"   -> Dateien: {len(files)} CSVs gefunden.")
            if len(files) > 0:
                print(f"   -> Beispiel: {files[0].name}")
            found_any = True
        else:
            print(f"❌ {name}: NICHT GEFUNDEN ({path})")

    print("-" * 50)

    # 3. Docker Check
    if os.path.exists("/app"):
        print("🐳 Umgebung: DOCKER-CONTAINER erkannt.")
    else:
        print("💻 Umgebung: LOKALER RECHNER (IntelliJ/Uvicorn) erkannt.")

    # 4. Empfehlung für application.properties
    if not found_any:
        print("\n🚨 WARNUNG: Keine ESCO-Daten gefunden! Stelle sicher, dass 'skills_de.csv' im Ordner 'data/esco' liegt.")
    else:
        rel_path = os.path.relpath(shared_data, root / "kotlin-api")
        print(f"\n💡 Empfehlung für Kotlin application.properties (IntelliJ):")
        print(f"   app.esco.data-path=../data/esco")

if __name__ == "__main__":
    check_system()
