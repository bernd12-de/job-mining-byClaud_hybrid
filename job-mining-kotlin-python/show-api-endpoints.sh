#!/bin/bash

# 🚀 Job Mining System - Startup Info Display
# Zeigt alle verfügbaren API-Endpunkte beim Container-Start

cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║                    🚀 JOB MINING SYSTEM - READY FOR ACTION                    ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝

📍 SERVER ENDPOINTS
─────────────────────────────────────────────────────────────────────────────────

  🔵 KOTLIN API (Spring Boot)
     URL: http://localhost:8080
     Health: http://localhost:8080/actuator/health
     Swagger: http://localhost:8080/swagger-ui.html

  🟢 PYTHON BACKEND (FastAPI)
     URL: http://localhost:8000
     Health: http://localhost:8000/system/status
     Docs: http://localhost:8000/docs

  📊 DASHBOARD (Streamlit)
     URL: http://localhost:8501

─────────────────────────────────────────────────────────────────────────────────

🔌 WICHTIGSTE API ENDPOINTS
─────────────────────────────────────────────────────────────────────────────────

  KOTLIN API (http://localhost:8080)
  ├── POST   /api/v1/jobs/scrape              Web-URL scrapen
  ├── POST   /api/v1/jobs/upload              PDF/DOCX hochladen
  ├── POST   /api/v1/jobs/batch-analyze       Batch-Verarbeitung
  ├── GET    /api/v1/jobs                     Alle Jobs abrufen
  ├── GET    /api/v1/jobs/reports/dashboard-metrics  📊 Dashboard-Daten
  ├── GET    /api/v1/rules/esco-full          ESCO-Wissensbasis
  └── GET    /api/discovery/candidates        Neue Kompetenzen

  PYTHON BACKEND (http://localhost:8000)
  ├── POST   /analyse/scrape-url               Scraping + Analyse
  ├── POST   /batch-process                    Alle lokalen Jobs
  ├── POST   /internal/admin/refresh-knowledge Knowledge reload
  └── GET    /system/status                    System-Status

─────────────────────────────────────────────────────────────────────────────────

🚀 QUICK START EXAMPLES
─────────────────────────────────────────────────────────────────────────────────

  1️⃣  Test Backend Health:
      curl http://localhost:8080/actuator/health | jq '.'
      curl http://localhost:8000/system/status | jq '.'

  2️⃣  Scrape URL mit JavaScript-Rendering:
      curl -X POST http://localhost:8080/api/v1/jobs/scrape \
        -H "Content-Type: application/json" \
        -d '{"url":"https://xing.com/jobs/..."}' \
        -G -d renderJs=true

  3️⃣  Batch-Verarbeitung starten:
      curl -X POST http://localhost:8000/batch-process | jq '.'

  4️⃣  Dashboard-Metriken abrufen:
      curl http://localhost:8080/api/v1/jobs/reports/dashboard-metrics | jq '.'

  5️⃣  Alle Jobs auflisten:
      curl http://localhost:8080/api/v1/jobs | jq '.[] | {title, jobRole}'

─────────────────────────────────────────────────────────────────────────────────

📁 WICHTIGE VERZEICHNISSE
─────────────────────────────────────────────────────────────────────────────────

  Data:
    • python-backend/data/jobs/                  ← Lokale Job-Dateien
    • python-backend/data/exports/batch_results/ ← Export-JSONs
    • data/fallback_rules/                       ← Mappings & Blacklist

  Docker:
    • docker-compose.yml / .v2.yml              ← Container-Setup
    • Dockerfile / Dockerfile.v2                ← Images
    • start.sh / QUICKSTART_V2.0.md             ← Startup-Guides

─────────────────────────────────────────────────────────────────────────────────

✅ SYSTEM CHECK
─────────────────────────────────────────────────────────────────────────────────

  Container Services:
    • PostgreSQL (jobmining_db)      [CHECK]
    • Kotlin API (8080)               [CHECK]
    • Python Backend (8000)           [CHECK]
    • Streamlit Dashboard (8501)      [OPTIONAL]

  Key Features:
    • JavaScript-Rendering (Playwright)  ✅
    • ESCO Knowledge Base               ✅ (async load)
    • Fallback Rule System              ✅
    • PDF/DOCX Support                  ✅
    • Batch Export (JSON)               ✅

─────────────────────────────────────────────────────────────────────────────────

📚 DOKUMENTATION
─────────────────────────────────────────────────────────────────────────────────

  API-Referenz:      ./API_ENDPOINTS.md
  Quickstart:        ./QUICKSTART_V2.0.md
  Setup-Guide:       ./SETUP_V2.0.md
  Dashboard Guide:   ./docs/DASHBOARD.md

─────────────────────────────────────────────────────────────────────────────────

🔐 ADMIN COMMANDS
─────────────────────────────────────────────────────────────────────────────────

  Clear ALL Data:
    curl -X DELETE http://localhost:8080/api/v1/jobs/admin/clear-all-data

  Sync Python Knowledge to Kotlin:
    curl -X POST http://localhost:8080/api/v1/jobs/admin/sync-python-knowledge

  Refresh Knowledge Base:
    curl -X POST http://localhost:8000/internal/admin/refresh-knowledge

─────────────────────────────────────────────────────────────────────────────────

💡 TIPPS
─────────────────────────────────────────────────────────────────────────────────

  • Alle Endpoints sind im Swagger UI dokumentiert: /swagger-ui.html
  • Python FastAPI Docs verfügbar unter: http://localhost:8000/docs
  • Batch-Jobs landen automatisch in: data/exports/batch_results/
  • Logs anschauen: docker logs <container-id>

═════════════════════════════════════════════════════════════════════════════════

Viel Erfolg! 🚀

EOF

# Prüfe ob Services laufen
echo ""
echo "🔍 Checking Service Status..."
echo ""

check_service() {
    local name=$1
    local url=$2
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo "  ✅ $name is UP"
    else
        echo "  ⏳ $name is starting... (retry in 10s)"
    fi
}

check_service "Kotlin API" "http://localhost:8080/actuator/health"
check_service "Python Backend" "http://localhost:8000/system/status"

echo ""
echo "Ready to work! 💪"
echo ""
