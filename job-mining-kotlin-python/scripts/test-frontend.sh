#!/bin/bash

# ============================================================================
# STREAMLIT MULTI-PAGE DASHBOARD - FRONTEND TESTS
# ============================================================================
# Testet das neue Streamlit Dashboard (Home.py + 5 Unterseiten)
#
# Features:
# - Service-Status Check (Python/Kotlin/DB/Streamlit)
# - Navigation Tests (alle 6 Seiten)
# - API Integration Tests
# - ESCO Data Loading (15.719 Skills)
# - Discovery Management Tests
# - Charts & Visualisierung Tests
#
# Verwendung:
#   ./scripts/test-frontend.sh
# ============================================================================

set -e

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API Endpoints (Auto-detect Docker vs. Lokal)
if [ -f "/.dockerenv" ] || [ "${DOCKER_CONTAINER}" = "true" ]; then
    PYTHON_API="http://python-backend:8000"
    KOTLIN_API="http://kotlin-api:8080"
    STREAMLIT_URL="http://streamlit:8501"
    echo -e "${BLUE}🐳 Docker-Umgebung erkannt${NC}"
else
    PYTHON_API="http://localhost:8000"
    KOTLIN_API="http://localhost:8080"
    STREAMLIT_URL="http://localhost:8501"
    echo -e "${BLUE}💻 Lokale Umgebung erkannt${NC}"
fi

# Zähler für Tests
TESTS_PASSED=0
TESTS_FAILED=0

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# ============================================================================
# 1. PRE-FLIGHT CHECKS
# ============================================================================
echo ""
echo "========================================================================"
echo "🚀 STREAMLIT DASHBOARD - FRONTEND TESTS"
echo "========================================================================"
echo ""

log_info "Prüfe ob erforderliche Tools installiert sind..."

# Check curl
if command -v curl &> /dev/null; then
    log_success "curl installiert"
else
    log_error "curl nicht gefunden (erforderlich für API-Tests)"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_success "Python $PYTHON_VERSION installiert"
else
    log_error "Python 3 nicht gefunden"
    exit 1
fi

# ============================================================================
# 2. SERVICE HEALTH CHECKS
# ============================================================================
echo ""
echo "========================================================================"
echo "🏥 SERVICE HEALTH CHECKS"
echo "========================================================================"
echo ""

# Python Backend
log_info "Teste Python Backend ($PYTHON_API)..."
if curl -s --max-time 5 "${PYTHON_API}/health" | grep -q "healthy"; then
    log_success "Python Backend läuft"
else
    log_error "Python Backend nicht erreichbar"
fi

# Kotlin Backend
log_info "Teste Kotlin Backend ($KOTLIN_API)..."
if curl -s --max-time 5 "${KOTLIN_API}/actuator/health" | grep -q "UP"; then
    log_success "Kotlin Backend läuft"
else
    log_error "Kotlin Backend nicht erreichbar"
fi

# Streamlit (wenn gestartet)
log_info "Teste Streamlit Dashboard ($STREAMLIT_URL)..."
if curl -s --max-time 5 "${STREAMLIT_URL}" > /dev/null 2>&1; then
    log_success "Streamlit Dashboard erreichbar"
else
    log_warning "Streamlit noch nicht gestartet (normal bei manuellem Start)"
fi

# ============================================================================
# 3. NAVIGATION TESTS (Dateien existieren)
# ============================================================================
echo ""
echo "========================================================================"
echo "📂 NAVIGATION TESTS"
echo "========================================================================"
echo ""

cd python-backend

# Home.py
if [ -f "Home.py" ]; then
    SIZE=$(stat -f%z "Home.py" 2>/dev/null || stat -c%s "Home.py")
    log_success "Home.py existiert (${SIZE} Bytes)"
else
    log_error "Home.py nicht gefunden"
fi

# Unterseiten
PAGES=(
    "pages/1_📈_Trends.py"
    "pages/2_👤_Rollen.py"
    "pages/3_🗺️_ESCO_Landkarte.py"
    "pages/4_🔍_Discovery.py"
    "pages/5_💼_Jobs.py"
)

for PAGE in "${PAGES[@]}"; do
    if [ -f "$PAGE" ]; then
        SIZE=$(stat -f%z "$PAGE" 2>/dev/null || stat -c%s "$PAGE")
        log_success "$(basename "$PAGE") existiert (${SIZE} Bytes)"
    else
        log_error "$(basename "$PAGE") nicht gefunden"
    fi
done

cd ..

# ============================================================================
# 4. PYTHON SYNTAX CHECK
# ============================================================================
echo ""
echo "========================================================================"
echo "🐍 PYTHON SYNTAX CHECKS"
echo "========================================================================"
echo ""

log_info "Prüfe Python-Syntax aller Dashboard-Dateien..."

cd python-backend

# Check Home.py
if python3 -m py_compile Home.py 2>/dev/null; then
    log_success "Home.py: Syntax OK"
else
    log_error "Home.py: Syntax-Fehler"
fi

# Check Unterseiten
for PAGE in "${PAGES[@]}"; do
    if python3 -m py_compile "$PAGE" 2>/dev/null; then
        log_success "$(basename "$PAGE"): Syntax OK"
    else
        log_error "$(basename "$PAGE"): Syntax-Fehler"
    fi
done

cd ..

# ============================================================================
# 5. API INTEGRATION TESTS
# ============================================================================
echo ""
echo "========================================================================"
echo "🔌 API INTEGRATION TESTS"
echo "========================================================================"
echo ""

# ESCO Skills
log_info "Teste ESCO Skills Endpoint..."
ESCO_COUNT=$(curl -s "${KOTLIN_API}/api/v1/rules/esco-full" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

if [ "$ESCO_COUNT" -gt 15000 ]; then
    log_success "ESCO Skills geladen: $ESCO_COUNT"
else
    log_error "ESCO Skills: Nur $ESCO_COUNT geladen (erwartet: ~15.719)"
fi

# Discovery Candidates
log_info "Teste Discovery Candidates Endpoint..."
DISCOVERY_RESPONSE=$(curl -s "${PYTHON_API}/discovery/candidates")

if echo "$DISCOVERY_RESPONSE" | grep -q "total"; then
    CANDIDATE_COUNT=$(echo "$DISCOVERY_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('total', 0))" 2>/dev/null || echo "0")
    log_success "Discovery Candidates: $CANDIDATE_COUNT"
else
    log_error "Discovery Endpoint nicht erreichbar"
fi

# Discovery Approved
log_info "Teste Discovery Approved Endpoint..."
if curl -s "${PYTHON_API}/discovery/approved" | grep -q "total"; then
    log_success "Discovery Approved: OK"
else
    log_error "Discovery Approved nicht erreichbar"
fi

# Jobs Endpoint (Kotlin)
log_info "Teste Jobs Endpoint..."
JOBS_RESPONSE=$(curl -s "${KOTLIN_API}/api/v1/jobs?page=0&size=10")

if echo "$JOBS_RESPONSE" | grep -q "\"content\""; then
    JOBS_COUNT=$(echo "$JOBS_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['content']))" 2>/dev/null || echo "0")
    log_success "Jobs Endpoint: $JOBS_COUNT Jobs geladen"
else
    log_error "Jobs Endpoint nicht erreichbar"
fi

# ============================================================================
# 6. CHART DATA GENERATION TESTS
# ============================================================================
echo ""
echo "========================================================================"
echo "📊 CHART DATA TESTS"
echo "========================================================================"
echo ""

log_info "Teste Chart-Daten-Generierung..."

# Test: Trend-Daten können generiert werden
python3 -c "
import sys
sys.path.append('python-backend')
try:
    from app.infrastructure.reporting import build_dashboard_metrics
    metrics = build_dashboard_metrics()

    # Check required fields
    required = ['total_jobs', 'total_skills', 'top_skills', 'time_series']
    missing = [f for f in required if f not in metrics]

    if missing:
        print(f'ERROR: Fehlende Felder: {missing}')
        sys.exit(1)
    else:
        print('SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
" 2>/dev/null

if [ $? -eq 0 ]; then
    log_success "Chart-Daten: Generierung erfolgreich"
else
    log_error "Chart-Daten: Generierung fehlgeschlagen"
fi

# ============================================================================
# 7. STREAMLIT SPECIFIC TESTS
# ============================================================================
echo ""
echo "========================================================================"
echo "🎨 STREAMLIT SPECIFIC TESTS"
echo "========================================================================"
echo ""

# Check streamlit installation
log_info "Prüfe Streamlit Installation..."
if python3 -c "import streamlit; print(streamlit.__version__)" 2>/dev/null; then
    STREAMLIT_VERSION=$(python3 -c "import streamlit; print(streamlit.__version__)")
    log_success "Streamlit $STREAMLIT_VERSION installiert"
else
    log_error "Streamlit nicht installiert (pip install streamlit)"
fi

# Check required packages für Dashboard
log_info "Prüfe Dashboard Dependencies..."

REQUIRED_PACKAGES=(
    "plotly"
    "pandas"
    "requests"
    "networkx"
)

for PKG in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $PKG" 2>/dev/null; then
        VERSION=$(python3 -c "import $PKG; print($PKG.__version__)" 2>/dev/null || echo "unknown")
        log_success "$PKG: $VERSION"
    else
        log_error "$PKG nicht installiert"
    fi
done

# ============================================================================
# 8. MEMORY & PERFORMANCE TESTS
# ============================================================================
echo ""
echo "========================================================================"
echo "⚡ PERFORMANCE TESTS"
echo "========================================================================"
echo ""

log_info "Messe Dashboard-Ladezeit..."

START_TIME=$(date +%s)

# Simuliere Dashboard-Load (API-Calls)
curl -s "${PYTHON_API}/health" > /dev/null 2>&1
curl -s "${KOTLIN_API}/actuator/health" > /dev/null 2>&1
curl -s "${PYTHON_API}/discovery/candidates" > /dev/null 2>&1

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

if [ "$DURATION" -lt 5 ]; then
    log_success "API-Calls: ${DURATION}s (schnell)"
elif [ "$DURATION" -lt 10 ]; then
    log_warning "API-Calls: ${DURATION}s (akzeptabel)"
else
    log_error "API-Calls: ${DURATION}s (zu langsam)"
fi

# ============================================================================
# 9. DISCOVERY MANAGEMENT TESTS
# ============================================================================
echo ""
echo "========================================================================"
echo "🔍 DISCOVERY MANAGEMENT TESTS"
echo "========================================================================"
echo ""

log_info "Teste Discovery Approve/Ignore Endpoints..."

# Test Approve (Mock)
APPROVE_RESPONSE=$(curl -s -X POST "${PYTHON_API}/discovery/approve" \
    -H "Content-Type: application/json" \
    -d '{"terms": ["test-skill"]}' 2>/dev/null || echo "ERROR")

if echo "$APPROVE_RESPONSE" | grep -q "success\|approved"; then
    log_success "Discovery Approve: OK"
else
    log_warning "Discovery Approve: Mock-Test (erwartet: realer Candidate)"
fi

# Test Ignore (Mock)
IGNORE_RESPONSE=$(curl -s -X POST "${PYTHON_API}/discovery/ignore" \
    -H "Content-Type: application/json" \
    -d '{"terms": ["test-skill"]}' 2>/dev/null || echo "ERROR")

if echo "$IGNORE_RESPONSE" | grep -q "success\|ignored"; then
    log_success "Discovery Ignore: OK"
else
    log_warning "Discovery Ignore: Mock-Test (erwartet: realer Candidate)"
fi

# ============================================================================
# 10. FINAL SUMMARY
# ============================================================================
echo ""
echo "========================================================================"
echo "📊 TEST SUMMARY"
echo "========================================================================"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))

echo -e "${GREEN}✅ Passed: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Failed: $TESTS_FAILED${NC}"
echo -e "${BLUE}📊 Total:  $TOTAL_TESTS${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALLE TESTS BESTANDEN!${NC}"
    echo ""
    echo "🚀 Dashboard starten mit:"
    echo "   cd python-backend && streamlit run Home.py"
    echo ""
    echo "📊 Dashboard URL:"
    echo "   $STREAMLIT_URL"
    exit 0
else
    echo -e "${RED}❌ EINIGE TESTS FEHLGESCHLAGEN${NC}"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Services prüfen:    curl $PYTHON_API/health"
    echo "   2. Logs einsehen:       docker logs streamlit"
    echo "   3. Neustart:            docker compose restart"
    exit 1
fi
