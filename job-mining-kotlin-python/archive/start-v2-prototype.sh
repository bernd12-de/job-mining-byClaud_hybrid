#!/bin/bash
# Skript zum optionalen Starten des V2-Prototyps

set -e

echo "════════════════════════════════════════════════════════════"
echo "🔄 V2-PROTOTYP REAKTIVIERUNG"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "⚠️  WARNUNG: Dies ist ein EXPERIMENTELLER Prototyp!"
echo "    Das produktive System läuft unter main.py"
echo ""

# Prüfe ob wir im richtigen Verzeichnis sind
if [ ! -d "archive/v2-prototype" ]; then
    echo "❌ Fehler: Muss im Hauptverzeichnis ausgeführt werden!"
    exit 1
fi

# Zeige Optionen
echo "Wähle eine Option:"
echo ""
echo "1) Demo-Script lokal starten (main_v2.py)"
echo "2) V2 mit Docker starten (docker-compose.v2.yml)"
echo "3) V2-Dateien ins Hauptverzeichnis kopieren (zum Testen)"
echo "4) Abbrechen"
echo ""
read -p "Deine Wahl [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "📋 Starte V2 Demo-Script..."
        echo ""
        
        # Temporär kopieren und ausführen
        cp archive/v2-prototype/main_v2.py python-backend/main_v2_temp.py
        cp archive/v2-prototype/models_v2.py python-backend/app/core/models_v2_temp.py
        
        # Script anpassen (models_v2_temp importieren)
        sed -i 's/from app.core.models_v2/from app.core.models_v2_temp/g' python-backend/main_v2_temp.py
        
        cd python-backend
        python3 main_v2_temp.py
        
        # Cleanup
        rm -f main_v2_temp.py app/core/models_v2_temp.py
        echo ""
        echo "✅ Demo beendet, temporäre Dateien entfernt"
        ;;
        
    2)
        echo ""
        echo "🐳 Starte V2 mit Docker..."
        echo ""
        
        # Docker-Files temporär kopieren
        cp archive/v2-prototype/docker-compose.v2.yml docker-compose.v2_temp.yml
        cp archive/v2-prototype/Dockerfile.v2 Dockerfile.v2_temp
        
        # Starte
        docker-compose -f docker-compose.v2_temp.yml up --build
        
        # Cleanup
        read -p "Docker-Container stoppen und Dateien entfernen? [y/n]: " cleanup
        if [ "$cleanup" = "y" ]; then
            docker-compose -f docker-compose.v2_temp.yml down
            rm -f docker-compose.v2_temp.yml Dockerfile.v2_temp
            echo "✅ Cleanup abgeschlossen"
        fi
        ;;
        
    3)
        echo ""
        echo "📂 Kopiere V2-Dateien..."
        
        # Backup erstellen
        if [ -f "python-backend/main_v2.py" ]; then
            echo "⚠️  main_v2.py existiert bereits!"
            read -p "Überschreiben? [y/n]: " overwrite
            if [ "$overwrite" != "y" ]; then
                echo "Abgebrochen"
                exit 0
            fi
        fi
        
        # Kopieren
        cp archive/v2-prototype/main_v2.py python-backend/
        cp archive/v2-prototype/models_v2.py python-backend/app/core/
        cp archive/v2-prototype/docker-compose.v2.yml .
        cp archive/v2-prototype/Dockerfile.v2 .
        
        echo ""
        echo "✅ V2-Dateien kopiert!"
        echo ""
        echo "Starten mit:"
        echo "  python python-backend/main_v2.py"
        echo "  ODER"
        echo "  docker-compose -f docker-compose.v2.yml up --build"
        echo ""
        echo "⚠️  WICHTIG: Diese Dateien sind NICHT ins Git eingecheckt!"
        echo "   Manuell wieder entfernen wenn fertig:"
        echo "   rm python-backend/main_v2.py python-backend/app/core/models_v2.py"
        echo "   rm docker-compose.v2.yml Dockerfile.v2"
        ;;
        
    4)
        echo "Abgebrochen"
        exit 0
        ;;
        
    *)
        echo "❌ Ungültige Auswahl"
        exit 1
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════════"
echo "ℹ️  Für produktiven Einsatz nutze: main.py (aktuelles System)"
echo "════════════════════════════════════════════════════════════"
