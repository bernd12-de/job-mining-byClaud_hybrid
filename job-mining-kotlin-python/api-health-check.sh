#!/bin/bash

# 🔍 API ENDPOINT HEALTH CHECK
# Überprüft beim Start, ob alle bekannten Endpoints erreichbar sind
# Schlägt Alarm wenn Endpoints "lost" sind (nicht erreichbar)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/api-health-check.log"
ENDPOINTS_FILE="${SCRIPT_DIR}/.api-endpoints-registry"

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

# ============================================================================
# SCHRITT 1: API-Endpoints Registry erstellen (einmalig)
# ============================================================================
create_endpoints_registry() {
    log "📋 Erstelle API-Endpoints Registry..."
    
    cat > "$ENDPOINTS_FILE" << 'EOF'
# Job Mining API - Endpoints Registry
# Generiert automatisch beim Setup
# Format: METHOD|PATH|DESCRIPTION|SERVICE

# KOTLIN API (Port 8080)
POST|/api/v1/jobs/upload|Upload PDF/DOCX Job-Dateien|kotlin
POST|/api/v1/jobs/scrape|Web-Scraping und Analyse|kotlin
POST|/api/v1/jobs/batch-analyze|Batch-Analyse lokaler Dateien|kotlin
GET|/api/v1/jobs|Alle analysierten Jobs abrufen|kotlin
GET|/api/v1/jobs/reports/dashboard-metrics|Dashboard-Statistiken|kotlin
GET|/api/v1/jobs/reports/competence-trends|Top Kompetenzen-Trends|kotlin
GET|/api/v1/jobs/reports/export.csv|CSV-Export|kotlin
GET|/api/v1/jobs/reports/export.pdf|PDF-Report|kotlin
GET|/api/v1/rules/blacklist|Blacklist abrufen|kotlin
GET|/api/v1/rules/role-mappings|Rollen-Mappings|kotlin
GET|/api/v1/rules/industry-mappings|Branchen-Mappings|kotlin
GET|/api/v1/rules/esco-full|Vollständige ESCO-Wissensbasis|kotlin
GET|/api/v1/rules/stats|Regelstatistiken|kotlin
GET|/api/discovery/candidates|Neue Kompetenzkandidaten|kotlin
GET|/api/discovery/approved|Approuvierte Kompetenzen|kotlin
GET|/api/discovery/ignore|Ignorierte Begriffe|kotlin
POST|/api/discovery/approve|Kompetenz genehmigen|kotlin
POST|/api/discovery/reject|Kompetenz ablehnen|kotlin
GET|/api/v1/jobs/admin/system-health|System-Status prüfen|kotlin
POST|/api/v1/jobs/admin/sync-python-knowledge|Knowledge synchronisieren|kotlin
DELETE|/api/v1/jobs/admin/clear-all-data|ALLE Daten löschen|kotlin
GET|/api/links|Alle Service-Links|kotlin
GET|/actuator/health|Spring Boot Health-Check|kotlin

# PYTHON BACKEND (Port 8000)
POST|/analyse/file|Lokale Datei analysieren|python
POST|/analyse/scrape-url|URL scrapen + NLP-Analyse|python
POST|/batch-process|Alle lokalen Jobs verarbeiten|python
GET|/system/status|Python-System Status|python
POST|/internal/admin/refresh-knowledge|Knowledge-Base neu laden|python
GET|/reports/dashboard-metrics|Dashboard-Metriken|python
GET|/docs|FastAPI Swagger UI|python
EOF
    
    log_success "Registry erstellt: $ENDPOINTS_FILE"
}

# ============================================================================
# SCHRITT 2: Health-Check für alle Endpoints
# ============================================================================
check_endpoint_health() {
    local method=$1
    local path=$2
    local service=$3
    local port=8080
    
    # Port basierend auf Service setzen
    if [ "$service" = "python" ]; then
        port=8000
    fi
    
    local url="http://localhost:${port}${path}"
    local timeout=5
    
    # Endpoint prüfen
    if curl -s -f -X "$method" "$url" -m "$timeout" > /dev/null 2>&1; then
        log_success "[$service:$port] $method $path"
        echo "UP"
        return 0
    else
        log_error "[$service:$port] $method $path - NOT RESPONDING"
        echo "DOWN"
        return 1
    fi
}

# ============================================================================
# SCHRITT 3: Warte auf Services
# ============================================================================
wait_for_service() {
    local service=$1
    local port=$2
    local max_retries=30
    local retry=0
    
    log "⏳ Warte auf $service ($port)..."
    
    while [ $retry -lt $max_retries ]; do
        if curl -s -f "http://localhost:${port}/actuator/health" > /dev/null 2>&1 || \
           curl -s -f "http://localhost:${port}/system/status" > /dev/null 2>&1 || \
           curl -s -f "http://localhost:${port}/" > /dev/null 2>&1; then
            log_success "$service ist READY"
            return 0
        fi
        
        retry=$((retry + 1))
        echo -n "."
        sleep 1
    done
    
    log_warn "$service ist NICHT ERREICHBAR nach $max_retries Sekunden"
    return 1
}

# ============================================================================
# SCHRITT 4: Haupt-Validierung
# ============================================================================
validate_all_endpoints() {
    log "🔍 Validiere alle registrierten Endpoints..."
    echo ""
    
    local total=0
    local success=0
    local failed=0
    local failed_endpoints=""
    
    # Lese Registry und prüfe jeden Endpoint
    while IFS='|' read -r method path description service; do
        # Überspringe Kommentare und leere Zeilen
        [[ "$method" =~ ^#.*$ ]] && continue
        [[ -z "$method" ]] && continue
        
        total=$((total + 1))
        
        local status=$(check_endpoint_health "$method" "$path" "$service")
        
        if [ "$status" = "UP" ]; then
            success=$((success + 1))
        else
            failed=$((failed + 1))
            failed_endpoints="${failed_endpoints}  - $method $path ($service)\n"
        fi
    done < "$ENDPOINTS_FILE"
    
    echo ""
    echo "════════════════════════════════════════════════════════════════════════"
    echo ""
    
    # Zusammenfassung
    local percentage=$((success * 100 / total))
    
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}✅ ALLE $success/$total ENDPOINTS ERREICHBAR${NC}"
        log_success "All endpoints validated: $success/$total UP"
        return 0
    else
        echo -e "${RED}❌ $failed/$total ENDPOINTS LOST (nicht erreichbar)${NC}"
        echo ""
        echo -e "${YELLOW}LOST ENDPOINTS:${NC}"
        echo -e "$failed_endpoints"
        log_error "$failed/$total endpoints DOWN - see details above"
        return 1
    fi
}

# ============================================================================
# SCHRITT 5: Generate Report
# ============================================================================
generate_report() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="${SCRIPT_DIR}/api-health-report-${timestamp// /-}.txt"
    
    log "📄 Generiere Health-Report..."
    
    {
        echo "╔════════════════════════════════════════════════════════════════════════════════╗"
        echo "║                   API HEALTH CHECK REPORT                                      ║"
        echo "╚════════════════════════════════════════════════════════════════════════════════╝"
        echo ""
        echo "Timestamp: $timestamp"
        echo "Host: $(hostname)"
        echo ""
        echo "═══════════════════════════════════════════════════════════════════════════════"
        echo ""
        tail -50 "$LOG_FILE"
        echo ""
        echo "═══════════════════════════════════════════════════════════════════════════════"
    } > "$report_file"
    
    log_success "Report gespeichert: $report_file"
}

# ============================================================================
# MAIN
# ============================================================================
main() {
    clear
    
    echo "╔════════════════════════════════════════════════════════════════════════════════╗"
    echo "║                  🔍 API ENDPOINT HEALTH CHECK                                  ║"
    echo "║                     Validiert alle registrierten APIs                          ║"
    echo "╚════════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Lösche alten Log
    > "$LOG_FILE"
    
    # Erstelle Registry wenn nicht vorhanden
    if [ ! -f "$ENDPOINTS_FILE" ]; then
        create_endpoints_registry
    fi
    
    # Warte auf Services
    wait_for_service "Kotlin API" 8080 &
    kotlin_pid=$!
    wait_for_service "Python Backend" 8000 &
    python_pid=$!
    
    wait $kotlin_pid 2>/dev/null || true
    wait $python_pid 2>/dev/null || true
    
    echo ""
    
    # Validiere alle Endpoints
    if validate_all_endpoints; then
        # Alles OK
        generate_report
        echo ""
        log_success "🚀 System bereit zum Arbeiten!"
        return 0
    else
        # Fehler gefunden
        generate_report
        echo ""
        log_error "⚠️  Einige Endpoints sind LOST - siehe Report oben"
        echo ""
        echo "🔧 Troubleshooting:"
        echo "  1. Überprüfe Docker-Logs:"
        echo "     docker logs kotlin-api"
        echo "     docker logs python-backend"
        echo ""
        echo "  2. Prüfe Services laufen:"
        echo "     docker ps | grep -E 'kotlin|python'"
        echo ""
        echo "  3. Restarte Services:"
        echo "     docker-compose restart"
        return 1
    fi
}

# Starte Main
main "$@"
