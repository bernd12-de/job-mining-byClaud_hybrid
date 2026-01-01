# IDE Setup Guide - Job Mining Kotlin-Python Hybrid

## 🚀 Quick Start

### 1. System starten
```bash
docker-compose up -d
```

### 2. Services überprüfen
```bash
# Alle Container sollten "Up" sein
docker ps

# Status aller Services testen
curl -s http://localhost:8080/api/links | jq
curl -s http://localhost:8000/system/status
docker exec job-mining-kotlin-python-jobmining-db-1 pg_isready -U jobmining_user
```

---

## 📍 Port Configuration

| Port | Service | Status | Access |
|------|---------|--------|--------|
| **8080** | Kotlin API (Swagger) | ✅ Läuft | `http://localhost:8080/swagger-ui/index.html` |
| **8000** | Python Backend API | ✅ Läuft | `http://localhost:8000/docs` |
| **5432** | PostgreSQL Database | ✅ Läuft | `localhost:5432` (intern) |
| **8501** | Streamlit Dashboard | ⚠️ Optional | `http://localhost:8501` |

---

## 🌐 Zugriff in VS Code Codespaces

### Option 1: Via Ports Panel (EMPFOHLEN)
1. Unten in VS Code auf **"Ports"** Panel klicken
2. Ports 8080, 8000 sehen
3. Auf den Globe-Icon neben dem Port klicken → Öffnet im Browser

### Option 2: Codespaces Public URLs
Nutze diese URLs um von außen zuzugreifen:
```
https://studious-space-fishstick-5g5gvqr6rggp349x4-8080.app.github.dev/swagger-ui/index.html
https://studious-space-fishstick-5g5gvqr6rggp349x4-8000.app.github.dev/docs
```
⚠️ **WICHTIG:** Ersetze `studious-space-fishstick-5g5gvqr6rggp349x4` mit deiner echten Codespaces URL!

### Option 3: Simple Browser (NICHT EMPFOHLEN)
- Der VS Code Simple Browser rendert JavaScript-Apps schlecht
- Nutze stattdessen die Options oben

---

## 🔧 Wichtige Operationen

### System Health Check
```bash
# Gesamtstatus abrufen
curl -s http://localhost:8080/api/v1/jobs/admin/system-health | jq
```

**Output sollte sein:**
```json
{
  "kotlin_backend": "ONLINE",
  "database": "CONNECTED",
  "python_worker": "ONLINE"
}
```

### Python Knowledge Refresh
```bash
curl -X POST http://localhost:8080/api/v1/jobs/admin/sync-python-knowledge
```

### Services Neustarten
```bash
# Einzelner Service
docker-compose restart python-backend

# Alle Services
docker-compose restart
```

---

## 📊 APIs im Detail

### Kotlin API (Port 8080)
**Swagger UI:** http://localhost:8080/swagger-ui/index.html

**Wichtige Endpoints:**
- `POST /api/v1/jobs/upload` - Stellenanzeige hochladen
- `POST /api/v1/jobs/scrape` - Web-URL scrapen
- `GET /api/v1/jobs` - Alle Jobs abrufen
- `GET /api/v1/rules/esco-full` - ESCO-Wissensbasis abrufen (15.682 Skills)
- `POST /api/v1/jobs/admin/sync-python-knowledge` - Python Knowledge Refresh

### Python Backend API (Port 8000)
**FastAPI Docs:** http://localhost:8000/docs

**Wichtige Endpoints:**
- `POST /analyse/file` - Datei analysieren
- `POST /analyse/scrape-url` - URL analysieren
- `GET /system/status` - System-Status
- `GET /role-mappings` - Rollen-Mappings abrufen

---

## 🐛 Troubleshooting

### Problem: Browser zeigt leere Seite
**Lösung:** 
- Nutze den **Ports Panel** (Globe Icon) statt Simple Browser
- Oder verwende die Codespaces Public URL

### Problem: Python Backend antwortet nicht
**Lösung:**
```bash
# Container neustarten
docker-compose restart python-backend

# Warten (braucht ~15 Sekunden zum vollständigen Start)
sleep 15

# Überprüfen
curl -s http://localhost:8000/system/status
```

### Problem: Ports sind belegt
**Lösung:**
```bash
# Alle Container stoppen
docker-compose down

# Ports freigeben und neu starten
docker-compose up -d
```

### Problem: Datenbank-Fehler
**Lösung:**
```bash
# DB neustarten und reset
docker-compose restart jobmining-db

# Warten auf Startup
sleep 5

# Verbindung testen
docker exec job-mining-kotlin-python-jobmining-db-1 pg_isready
```

---

## 💾 Datenbank (PostgreSQL)

**Credentials:**
```
Host: localhost
Port: 5432
Database: jobmining_db
User: jobmining_user
Password: secret_password
```

**Via psql verbinden:**
```bash
docker exec -it job-mining-kotlin-python-jobmining-db-1 psql -U jobmining_user -d jobmining_db
```

**Häufige Queries:**
```sql
-- Jobs zählen
SELECT COUNT(*) FROM job_posting;

-- Top Skills
SELECT competence_label, COUNT(*) FROM competence GROUP BY competence_label ORDER BY COUNT(*) DESC LIMIT 10;

-- Jobs mit Datum
SELECT title, posting_date FROM job_posting ORDER BY posting_date DESC LIMIT 5;
```

---

## 📝 Docker Compose Struktur

```yaml
Services im docker-compose.yml:

1. kotlin-api:8080        → Spring Boot API Gateway
2. python-backend:8000    → FastAPI Analyse-Engine
3. jobmining-db:5432      → PostgreSQL Datenbank
4. streamlit:8501         → Visualisierung & Dashboard (optional)
```

**Ports in docker-compose.yml:**
- Alle Services haben `ports: ["HOST:CONTAINER"]` definiert
- Damit sind sie von außen (Codespaces) erreichbar
- Intern kommunizieren Services über Containernamen

---

## 🎯 Typischer Workflow

1. **System starten**
   ```bash
   docker-compose up -d
   sleep 20  # Warte auf vollständigen Start
   ```

2. **Health Check**
   ```bash
   curl -s http://localhost:8080/api/v1/jobs/admin/system-health | jq
   ```

3. **API testen**
   - Öffne http://localhost:8080/swagger-ui/index.html (via Ports Panel)
   - Oder http://localhost:8000/docs für Python API

4. **Job analysieren**
   - Datei hochladen via Kotlin Swagger UI
   - Oder REST-Call testen via Python Docs

5. **Ergebnisse anschauen**
   - `GET /api/v1/jobs` in Swagger
   - oder `GET /api/v1/jobs` in Python FastAPI

---

## 🔗 Nützliche Links

- **Kotlin Spring Boot Docs** → http://localhost:8080/swagger-ui/index.html
- **Python FastAPI Docs** → http://localhost:8000/docs
- **OpenAPI Spec (Kotlin)** → http://localhost:8080/v3/api-docs
- **OpenAPI Spec (Python)** → http://localhost:8000/openapi.json

---

## ⚠️ Known Issues

| Issue | Status | Workaround |
|-------|--------|-----------|
| Streamlit Dashboard startet nicht | ⚠️ Optional | Nicht kritisch, APIs funktionieren |
| Simple Browser zeigt JavaScript leer | ✅ Bekannt | Nutze Ports Panel Globe Icon |
| Python braucht Zeit zum Starten | ✅ Normal | Warten Sie 15-20 Sekunden |

---

## 📅 Last Updated
27.12.2025 - System vollständig funktionsfähig ✅

**Status:**
- ✅ Kotlin API (Port 8080)
- ✅ Python Backend (Port 8000)  
- ✅ PostgreSQL (Port 5432)
- ⚠️ Streamlit Dashboard (optional)
