# 📚 API-Dokumentation - Job Mining System

Diese Dokumentation enthält **alle API-Endpunkte** in verschiedenen Formaten, damit sie nicht verloren gehen.

## 📂 Verfügbare Dokumentations-Formate

| Format | Datei | Zweck | Verbesserungen |
|--------|-------|-------|---|
| 📖 **Markdown** | [`API_ENDPOINTS.md`](./API_ENDPOINTS.md) | Lesbar, strukturiert, GitHub-Integration | Mit Beispielen & Tabellen |
| 📄 **Plain Text** | [`API_ENDPOINTS.txt`](./API_ENDPOINTS.txt) | Für Konsole/Terminal, cat-bar | Vollständige Referenz |
| 🌐 **HTML** | [`api-reference.html`](./api-reference.html) | Browser-Anzeige, interaktiv | Mit Farben & Layout |
| 🔧 **Bash Script** | [`show-api-endpoints.sh`](./show-api-endpoints.sh) | Beim Docker-Start ausführen | ASCII-Art + Service-Check |

## 🚀 Schneller Zugriff

### 1️⃣ Alle Endpoints im Browser sehen
```bash
# HTML-Version im Browser öffnen
open api-reference.html  # macOS
# oder
firefox api-reference.html  # Linux
```

### 2️⃣ Endpoints in der Konsole anzeigen
```bash
# Alle Endpoints als formatierter Text
cat API_ENDPOINTS.txt

# Mit Bash-Script (mit Service-Check)
./show-api-endpoints.sh

# Oder einfach: Markdown anzeigen
cat API_ENDPOINTS.md
```

### 3️⃣ Swagger UI (Best Practice!)
```bash
# Im Browser öffnen:
http://localhost:8080/swagger-ui.html

# Oder direkter API-Docs:
http://localhost:8000/docs  # Python FastAPI
```

---

## 📍 Haupt-Dokumentation

### Kotlin API (Port 8080)
**18 Endpunkte** über 5 Kategorien:
- **Job Management** (4): upload, scrape, batch-analyze, list
- **Reports** (4): dashboard-metrics, trends, CSV, PDF
- **Rule Management** (5): blacklist, role-mappings, industry-mappings, esco-full, stats
- **Discovery** (3): candidates, approved, ignore (+ post/approve/reject)
- **Admin** (3): system-health, sync-knowledge, clear-data

### Python Backend (Port 8000)
**7 Endpunkte** über 3 Kategorien:
- **Analysis** (3): file, scrape-url, batch-process
- **Knowledge** (2): system-status, refresh-knowledge
- **Reports** (2): dashboard-metrics, export-metrics

---

## 💾 Wo landen die Daten?

```
python-backend/
├── data/
│   ├── jobs/                    ← Input: PDF/DOCX Stellenanzeigen
│   └── exports/
│       └── batch_results/       ← Output: JSON-Analysen
└── requirements.txt             ← Python Dependencies

kotlin-api/
├── build.gradle.kts             ← Kotlin Dependencies
└── src/main/kotlin/
    └── de/layher/jobmining/
        └── config/
            ├── GlobalExceptionHandler.kt    ← Error Handling
            └── DependencyCheckConfig.kt     ← System Checks
```

---

## 🔍 Endpoint-Beispiele

### Scrape mit JS-Rendering
```bash
curl -X POST "http://localhost:8080/api/v1/jobs/scrape?renderJs=true" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.xing.com/jobs/berlin-senior-designer"}'
```

### Batch verarbeiten
```bash
curl -X POST http://localhost:8000/batch-process | jq '.[] | {title, competences}'
```

### Dashboard-Daten holen
```bash
curl "http://localhost:8080/api/v1/jobs/reports/dashboard-metrics?top_n=20" | jq '.'
```

### Alle Jobs auflisten
```bash
curl http://localhost:8080/api/v1/jobs | jq '.[] | {title, region, industry, jobRole}'
```

---

## ⚠️ Wichtige Admin-Operationen

### System-Status prüfen
```bash
curl http://localhost:8080/actuator/health
curl http://localhost:8000/system/status
```

### Knowledge-Base neu laden
```bash
curl -X POST http://localhost:8000/internal/admin/refresh-knowledge
```

### ALLE Daten löschen (⚠️ VORSICHT!)
```bash
curl -X DELETE http://localhost:8080/api/v1/jobs/admin/clear-all-data
```

---

## 📊 Dokumentation aktualisieren

Diese Dateien sollten **nach API-Änderungen** aktualisiert werden:

1. **API_ENDPOINTS.md** - User-friendly Markdown
2. **API_ENDPOINTS.txt** - Plain Text für Konsole
3. **api-reference.html** - HTML mit Styling
4. **show-api-endpoints.sh** - Bash-Output

**Quick Update mit einem Script:**
```bash
# Swagger API-Docs abfragen
curl http://localhost:8080/v3/api-docs | jq '.'

# Neue Endpoints extrahieren
curl http://localhost:8080/v3/api-docs | jq '.paths | keys'
```

---

## 🛠️ Integration mit Docker

**In `docker-compose.yml` hinzufügen (optional):**
```yaml
volumes:
  - ./API_ENDPOINTS.md:/docs/API_ENDPOINTS.md
  - ./api-reference.html:/usr/share/nginx/html/api-reference.html
```

**Beim Start anzeigen:**
```yaml
services:
  kotlin-api:
    ...
    command: >
      sh -c "
        bash show-api-endpoints.sh &&
        java -jar build/libs/kotlin-api-0.0.1-SNAPSHOT.jar
      "
```

---

## 🔗 Verwandte Dokumentation

| Datei | Beschreibung |
|-------|-------------|
| [README.md](./README.md) | Projekt-Übersicht |
| [QUICKSTART_V2.0.md](./QUICKSTART_V2.0.md) | Schneller Start |
| [SETUP_V2.0.md](./SETUP_V2.0.md) | Detaillierter Setup |
| [docs/DASHBOARD.md](./docs/DASHBOARD.md) | Dashboard-Guide |

---

## ✅ Checkliste für neue Developer

- [ ] `API_ENDPOINTS.md` gelesen
- [ ] `api-reference.html` im Browser angesehen
- [ ] Swagger UI getestet (http://localhost:8080/swagger-ui.html)
- [ ] Erste API-Calls getestet (siehe Beispiele oben)
- [ ] System-Health überprüft
- [ ] Dashboard-Metriken angesehen

---

**Zuletzt aktualisiert:** 2025-12-27  
**Version:** 2.0 (Production Ready)

Fragen? → Check Swagger UI oder run: `./show-api-endpoints.sh`
