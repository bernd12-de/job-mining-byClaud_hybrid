#!/bin/bash
# Start Script für Job Mining V2.0 mit optionalem Dashboard
# Mit umfassender Fehlerbehandlung

# Fehlerbehandlung aktivieren (aber nicht mehr set -e, da wir Fehler abfangen wollen)
set -o pipefail

# Funktion für sauberes Error-Handling
error_exit() {
    echo "❌ FEHLER: $1" >&2
    echo "ℹ️  Überprüfen Sie die Logs für weitere Details."
    exit 1
}

# Funktion für sichere Kommando-Ausführung
safe_execute() {
    local cmd="$1"
    local error_msg="$2"
    
    if ! eval "$cmd"; then
        if [ -n "$error_msg" ]; then
            echo "⚠️  $error_msg"
        fi
        return 1
    fi
    return 0
}

echo "════════════════════════════════════════════════════════════"
echo "🚀 JOB MINING HYBRID APPLICATION V2.0 - START"
echo "════════════════════════════════════════════════════════════"
echo ""

# Parse arguments
DASHBOARD=false
DOCKER=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dashboard)
            DASHBOARD=true
            shift
            ;;
        --docker)
            DOCKER=true
            shift
            ;;
        *)
            echo "⚠️  Unbekannte Option: $1"
            echo "Verwendung: $0 [--dashboard] [--docker]"
            exit 1
            ;;
    esac
done

# Check Python
if ! command -v python3 &> /dev/null; then
    error_exit "Python 3 nicht gefunden! Bitte installieren Sie Python 3.8 oder höher."
fi

echo "✅ Python Version: $(python3 --version)"
echo ""

# Check/Install dependencies
echo "📦 Prüfe Dependencies..."
if [ ! -d "venv" ]; then
    echo "  Erstelle venv..."
    if ! python3 -m venv venv; then
        error_exit "Konnte venv nicht erstellen. Ist python3-venv installiert?"
    fi
fi

# Activate venv
if ! source venv/bin/activate; then
    error_exit "Konnte venv nicht aktivieren"
fi

echo "  Installiere Packages..."
if [ -f "python-backend/requirements.txt" ]; then
    pip install -q -r python-backend/requirements.txt || {
        echo "⚠️  Einige Packages konnten nicht installiert werden"
        echo "   System läuft weiter mit vorhandenen Packages..."
    }
elif [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt || {
        echo "⚠️  Einige Packages konnten nicht installiert werden"
        echo "   System läuft weiter mit vorhandenen Packages..."
    }
else
    echo "⚠️  Keine requirements.txt gefunden"
fi

# Download spaCy model if not present
echo "  Prüfe spaCy Modell..."
if ! python3 -c "import spacy; spacy.load('de_core_news_md')" 2>/dev/null; then
    echo "  Lade spaCy Modell herunter..."
    if ! python3 -m spacy download de_core_news_md; then
        echo "⚠️  Konnte de_core_news_md nicht laden, versuche de_core_news_sm..."
        if ! python3 -m spacy download de_core_news_sm; then
            echo "⚠️  Warnung: Konnte kein spaCy Modell laden"
            echo "   NLP-Funktionen könnten eingeschränkt sein"
        fi
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "🔧 KONFIGURATION"
echo "════════════════════════════════════════════════════════════"
echo "  Dashboard: $([ "$DASHBOARD" = true ] && echo "✅ AKTIVIERT" || echo "❌ DEAKTIVIERT")"
echo "  Docker:    $([ "$DOCKER" = true ] && echo "✅ AKTIVIERT" || echo "❌ DEAKTIVIERT")"
echo ""

# Start based on configuration
if [ "$DOCKER" = true ]; then
    echo "🐳 Starte mit Docker..."
    echo ""
    if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
        error_exit "Docker/Docker-Compose nicht gefunden!"
    fi
    
    if [ -f "docker-compose.v2.yml" ]; then
        docker-compose -f docker-compose.v2.yml up --build || error_exit "Docker-Start fehlgeschlagen"
    else
        error_exit "docker-compose.v2.yml nicht gefunden"
    fi
    
elif [ "$DASHBOARD" = true ]; then
    echo "📊 Starte mit Dashboard..."
    echo ""
    
    # Start both API and Dashboard
    if [ -f "python-backend/app/api/dashboard_api.py" ]; then
        python3 python-backend/app/api/dashboard_api.py &
        API_PID=$!
    elif [ -f "app/api/dashboard_api.py" ]; then
        python3 app/api/dashboard_api.py &
        API_PID=$!
    else
        echo "⚠️  Dashboard-API nicht gefunden, fahre trotzdem fort..."
    fi
    
    sleep 2
    echo ""
    echo "🌐 Dashboard verfügbar unter: http://localhost:5000/dashboard"
    echo "ℹ️  Drücken Sie Ctrl+C zum Beenden"
    echo ""
    
    # Trap für sauberes Herunterfahren
    trap "echo ''; echo '🛑 Beende Dienste...'; kill $API_PID 2>/dev/null; exit 0" INT TERM
    
    wait $API_PID 2>/dev/null || echo "⚠️  Dashboard-Prozess wurde beendet"
    
else
    echo "🔨 Starte Core Pipeline..."
    echo ""
    
    # Versuche main_v2.py zu finden
    if [ -f "python-backend/main_v2.py" ]; then
        python3 python-backend/main_v2.py || echo "⚠️  Pipeline mit Fehlern beendet"
    elif [ -f "main_v2.py" ]; then
        python3 main_v2.py || echo "⚠️  Pipeline mit Fehlern beendet"
    else
        error_exit "main_v2.py nicht gefunden"
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ FINISHED"
echo "════════════════════════════════════════════════════════════"
