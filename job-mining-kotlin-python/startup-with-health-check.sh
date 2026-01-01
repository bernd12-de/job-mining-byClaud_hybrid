#!/bin/bash

# ╔════════════════════════════════════════════════════════════════════════════════╗
# ║  Job Mining - Startup mit Port-Cleanup & Health-Check                        ║
# ║  Automatisches Port-Management, Docker-Start, Endpoint-Validierung           ║
# ╚════════════════════════════════════════════════════════════════════════════════╝

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ============================================================================
# Check + Cleanup Ports
# ============================================================================

check_and_cleanup_ports() {
    echo "[1/4] 🔍 Prüfe Port-Verfügbarkeit..."
    echo ""
    
    local ports=(8000 8080 8501 5432)
    local blocked=()
    
    # Prüfe Ports
    for port in "${ports[@]}"; do
        if lsof -i :$port >/dev/null 2>&1; then
            blocked+=("$port")
        fi
    done
    
    # Keine Probleme
    if [ ${#blocked[@]} -eq 0 ]; then
        echo "✅ Alle Ports verfügbar"
        echo ""
        return 0
    fi
    
    # Ports sind belegt
    echo -e "${YELLOW}⚠️  Folgende Ports belegt: ${blocked[*]}${NC}"
    echo ""
    
    # Versuche docker-compose down
    echo "🐳 Versuche Docker-Services zu stoppen..."
    docker-compose down 2>/dev/null || true
    sleep 3
    
    # Prüfe erneut
    local still_blocked=()
    for port in "${blocked[@]}"; do
        if lsof -i :$port >/dev/null 2>&1; then
            still_blocked+=("$port")
        fi
    done
    
    if [ ${#still_blocked[@]} -eq 0 ]; then
        echo "✅ Ports jetzt verfügbar"
        echo ""
        return 0
    fi
    
    # Force-kill
    echo -e "${YELLOW}⚠️  Force-Kill läuft...${NC}"
    for port in "${still_blocked[@]}"; do
        local pid=$(lsof -ti :$port 2>/dev/null | head -1)
        if [ -n "$pid" ]; then
            echo "  Killing PID $pid (Port $port)"
            kill -9 "$pid" 2>/dev/null || true
        fi
    done
    sleep 2
    
    # Final check
    local final_blocked=()
    for port in "${still_blocked[@]}"; do
        if lsof -i :$port >/dev/null 2>&1; then
            final_blocked+=("$port")
        fi
    done
    
    if [ ${#final_blocked[@]} -gt 0 ]; then
        echo -e "${RED}❌ FEHLER: Ports noch belegt: ${final_blocked[*]}${NC}"
        echo ""
        return 1
    fi
    
    echo "✅ Ports jetzt verfügbar"
    echo ""
    return 0
}

# ============================================================================
# Main
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║  🚀 JOB MINING SYSTEM STARTUP                                                 ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Schritt 1: Port-Cleanup
if ! check_and_cleanup_ports; then
    exit 1
fi

# Schritt 2: Docker starten
echo "[2/4] 🐳 Starte Docker Services..."
cd "$SCRIPT_DIR"
docker-compose up -d 2>&1 | grep -E "Running|Created|Started|Error" || true
echo "✅ Docker Services gestartet"
echo ""

# Schritt 3: Warte
echo "[3/4] ⏳ Warte auf Services (10 Sekunden)..."
sleep 10
echo "✅ Services sollten jetzt bereit sein"
echo ""

# Schritt 4: Health-Check
echo "[4/4] 🔍 Führe Health-Check durch..."
echo ""

if [ -x "$SCRIPT_DIR/api-health-check.sh" ]; then
    bash "$SCRIPT_DIR/api-health-check.sh" 2>&1 | tail -60
    HEALTH_STATUS=$?
    
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════════════════╗"
    if [ $HEALTH_STATUS -eq 0 ]; then
        echo "║  ✅ SYSTEM BEREIT                                                            ║"
        echo "╚════════════════════════════════════════════════════════════════════════════════╝"
        echo ""
        echo "📊 Dashboard:  http://localhost:8501"
        echo "🔌 Kotlin API: http://localhost:8080"
        echo "🐍 Python:     http://localhost:8000"
        echo "📚 Swagger:    http://localhost:8080/swagger-ui.html"
        echo ""
        exit 0
    else
        echo "║  ⚠️  HEALTH-CHECK FEHLGESCHLAGEN                                              ║"
        echo "╚════════════════════════════════════════════════════════════════════════════════╝"
        echo ""
        echo "Befehle zum Debuggen:"
        echo "  docker ps          # Zeige Container"
        echo "  docker-compose logs -f kotlin-api"
        echo "  docker-compose logs -f python-backend"
        echo "  docker-compose restart"
        echo ""
        exit 1
    fi
else
    echo "⚠️  Health-Check Script nicht gefunden"
    exit 1
fi
