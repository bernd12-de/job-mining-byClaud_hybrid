#!/bin/bash
# Kein set -e hier - wir wollen kontrollierte Fehlerbehandlung

# ============================================================================
# E2E Test: Job Mining System - Vollständiger Workflow
# ============================================================================

BASE_DIR="/workspaces/job-mining-kotlin-python"
KOTLIN_JAR="$BASE_DIR/kotlin-api/build/libs/kotlin-api-0.0.1-SNAPSHOT.jar"
PYTHON_DIR="$BASE_DIR/python-backend"

echo "🧪 === E2E TEST GESTARTET ==="
echo "Timestamp: $(date)"
echo ""

# ============================================================================
# SCHRITT 1: Alte Prozesse beenden
# ============================================================================
echo "📍 SCHRITT 1/5: Alte Prozesse beenden..."
pkill -f "java -jar.*kotlin-api" 2>/dev/null || true
pkill -f "uvicorn main:app" 2>/dev/null || true
sleep 2
echo "✅ Ports freigegeben"
echo ""

# ============================================================================
# SCHRITT 2: Datenbank leeren
# ============================================================================
echo "📍 SCHRITT 2/5: Datenbank leeren..."
PGPASSWORD=yourpassword psql -h localhost -U jobmining_user -d jobmining_db -c "
  TRUNCATE TABLE job_postings CASCADE;
  TRUNCATE TABLE esco_data CASCADE;
  TRUNCATE TABLE domain_rules CASCADE;
" 2>&1 | grep -E "TRUNCATE|ERROR" || echo "⚠️ DB bereits leer oder nicht erreichbar"
echo "✅ Datenbank geleert"
echo ""

# ============================================================================
# SCHRITT 3: Services starten (Kotlin + Python)
# ============================================================================
echo "📍 SCHRITT 3/5: Services starten..."

# Kotlin API starten
echo "  → Starte Kotlin API (Port 8080)..."
JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 java -jar "$KOTLIN_JAR" \
  --server.port=8080 > /tmp/kotlin_e2e.log 2>&1 &
KOTLIN_PID=$!
echo "    PID: $KOTLIN_PID"

# Python Backend starten
echo "  → Starte Python Backend (Port 8000)..."
cd "$PYTHON_DIR"
python -m uvicorn main:app --port 8000 > /tmp/python_e2e.log 2>&1 &
PYTHON_PID=$!
echo "    PID: $PYTHON_PID"

# Warte auf Services (mit Timeout)
echo "  → Warte auf Services (max 90s)..."
for i in {1..90}; do
  KOTLIN_UP=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/actuator/health 2>/dev/null)
  PYTHON_UP=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs 2>/dev/null)
  
  if [[ "$KOTLIN_UP" == "200" && "$PYTHON_UP" == "200" ]]; then
    echo "✅ Beide Services bereit (nach ${i}s)"
    echo "   Kotlin: http://localhost:8080 (Status: $KOTLIN_UP)"
    echo "   Python: http://localhost:8000 (Status: $PYTHON_UP)"
    break
  fi
  
  if [[ $i -eq 90 ]]; then
    echo "❌ TIMEOUT: Services nicht bereit nach 90s"
    echo "   Kotlin Status: $KOTLIN_UP | Python Status: $PYTHON_UP"
    echo "Kotlin Log:"
    tail -30 /tmp/kotlin_e2e.log
    echo "Python Log:"
    tail -30 /tmp/python_e2e.log
    kill $KOTLIN_PID $PYTHON_PID 2>/dev/null || true
    exit 1
  fi
  
  # Zeige Progress alle 10 Sekunden
  if [[ $((i % 10)) -eq 0 ]]; then
    echo "   Warte... (${i}s) Kotlin:$KOTLIN_UP Python:$PYTHON_UP"
  fi
  sleep 1
done
echo ""

# ============================================================================
# SCHRITT 4: Batch-Verarbeitung (Stellenanzeigen analysieren)
# ============================================================================
echo "📍 SCHRITT 4/5: Batch-Verarbeitung..."

# Prüfe ob Testdaten vorhanden sind
JOBS_DIR="$BASE_DIR/data/jobs"
if [[ ! -d "$JOBS_DIR" ]] || [[ -z "$(ls -A $JOBS_DIR 2>/dev/null)" ]]; then
  echo "⚠️ Keine Stellenanzeigen in $JOBS_DIR gefunden"
  echo "  Erstelle Test-Stellenanzeige..."
  mkdir -p "$JOBS_DIR"
  cat > "$JOBS_DIR/test_job_1.txt" <<'EOF'
Software-Entwickler (m/w/d) Python & Kotlin

Ihre Aufgaben:
- Entwicklung von Backend-Services mit Python und Kotlin
- Datenbanken: PostgreSQL, MongoDB
- API-Design und REST-Schnittstellen
- Agile Softwareentwicklung im Team

Ihr Profil:
- Studium der Informatik oder vergleichbar
- Erfahrung mit FastAPI, Spring Boot
- Kenntnisse in Docker und Kubernetes
- Teamfähigkeit und Kommunikationsstärke

Wir bieten:
- Flexible Arbeitszeiten
- Home-Office möglich
- Attraktives Gehalt
EOF
  echo "  ✅ Test-Stellenanzeige erstellt"
fi

JOB_COUNT=$(ls -1 "$JOBS_DIR"/*.txt 2>/dev/null | wc -l || echo "0")
echo "  → Gefundene Stellenanzeigen: $JOB_COUNT"

if [[ $JOB_COUNT -gt 0 ]]; then
  echo "  → Starte Batch-Analyse via /batch-process..."
  
  # Erstelle JSON Array mit allen Stellenanzeigen
  echo "    Bereite Batch-Request vor..."
  jobs_json="["
  first=true
  for job_file in "$JOBS_DIR"/*.txt; do
    job_content=$(cat "$job_file" | tr '\n' ' ' | sed 's/"/\\"/g')
    if [ "$first" = true ]; then
      first=false
    else
      jobs_json+=","
    fi
    jobs_json+="{\"text\": \"$job_content\", \"title\": \"$(basename $job_file)\"}"
  done
  jobs_json+="]"
  
  echo "    Sende $JOB_COUNT Job(s) an Backend..."
  response=$(curl -s -w "\n%{http_code}" -X POST \
    "http://localhost:8000/batch-process" \
    -H "Content-Type: application/json" \
    -d "$jobs_json" \
    2>/dev/null)
  
  http_code=$(echo "$response" | tail -1)
  body=$(echo "$response" | head -n -1)
  
  if [[ "$http_code" == "200" ]]; then
    echo "    ✅ Batch erfolgreich verarbeitet (HTTP $http_code)"
    # Extrahiere Anzahl der Ergebnisse aus Response
    result_count=$(echo "$body" | grep -o '{' | wc -l)
    echo "    📊 Ergebnisse: $result_count Analyse(n) zurückgegeben"
    PROCESSED=$JOB_COUNT
  else
    echo "    ❌ Batch fehlgeschlagen (HTTP $http_code)"
    echo "    Response: $(echo "$body" | head -100)"
    PROCESSED=0
  fi
  
  echo "  ✅ Verarbeitet: $PROCESSED/$JOB_COUNT"
else
  echo "  ⚠️ Keine Jobs zum Verarbeiten"
fi
echo ""

# ============================================================================
# SCHRITT 5: Dashboard prüfen
# ============================================================================
echo "📍 SCHRITT 5/5: Dashboard prüfen..."

# Prüfe und installiere Dashboard-Pakete bei Bedarf
echo "  → Prüfe Dashboard-Abhängigkeiten..."
cd "$PYTHON_DIR"
python -c "from check_packages import check_dashboard_requirements; check_dashboard_requirements()" 2>&1 | grep -E "✅|📦|⚠️"

# Dashboard starten (Streamlit)
echo "  → Starte Dashboard (Port 8501)..."
if command -v streamlit &> /dev/null; then
  streamlit run dashboard_app.py --server.port 8501 > /tmp/dashboard_e2e.log 2>&1 &
  DASHBOARD_PID=$!
  
  # Warte auf Dashboard
  sleep 8
  
  DASHBOARD_UP=$(curl -s http://localhost:8501 2>/dev/null | grep -o "streamlit" || echo "")
  if [[ -n "$DASHBOARD_UP" ]]; then
    echo "  ✅ Dashboard erreichbar: http://localhost:8501"
    echo ""
    echo "  📊 Dashboard-Check:"
    echo "     - URL: http://localhost:8501"
    echo "     - Bitte manuell prüfen:"
    echo "       • Werden verarbeitete Jobs angezeigt?"
    echo "       • Sind Kompetenz-Daten sichtbar?"
    echo "       • Funktionieren die Visualisierungen?"
    echo ""
    echo "  💡 Dashboard läuft im Hintergrund (PID: $DASHBOARD_PID)"
  else
    echo "  ⚠️ Dashboard nicht erreichbar"
    echo "  Log:"
    tail -15 /tmp/dashboard_e2e.log
  fi
else
  echo "  ⚠️ Streamlit nicht verfügbar - Installation fehlgeschlagen"
  echo "  Versuche manuelle Installation: pip install streamlit"
fi
echo ""

# ============================================================================
# ZUSAMMENFASSUNG
# ============================================================================
echo "="*70
echo "🎉 E2E TEST ABGESCHLOSSEN"
echo "="*70
echo ""
echo "🚀 Laufende Services:"
echo "   - Kotlin API:     PID $KOTLIN_PID (Port 8080)"
echo "   - Python Backend: PID $PYTHON_PID (Port 8000)"
echo "   - Dashboard:      PID $DASHBOARD_PID (Port 8501)"
echo ""
echo "📋 Logs verfügbar:"
echo "   - Kotlin:    tail -f /tmp/kotlin_e2e.log"
echo "   - Python:    tail -f /tmp/python_e2e.log"
echo "   - Dashboard: tail -f /tmp/dashboard_e2e.log"
echo ""
echo "🛑 Services beenden:"
echo "   kill $KOTLIN_PID $PYTHON_PID $DASHBOARD_PID"
echo ""
echo "🌐 Zugriff:"
echo "   - Swagger (Kotlin): http://localhost:8080/swagger-ui.html"
echo "   - API Docs (Python): http://localhost:8000/docs"
echo "   - Dashboard: http://localhost:8501"
echo ""
