# 🚀 Job Mining API - Alle Endpoints

**Generiert:** 2025-12-27 | **Version:** 2.0

---

## 📍 Server URLs

| Service | URL | Status |
|---------|-----|--------|
| **Kotlin API** | `http://localhost:8080` | Main API |
| **Python Backend** | `http://localhost:8000` | NLP/Scraping |
| **Swagger UI** | `http://localhost:8080/swagger-ui.html` | API-Docs |
| **Python Docs** | `http://localhost:8000/docs` | FastAPI Docs |
| **Dashboard** | `http://localhost:8501` | Streamlit |

---

## 🔌 KOTLIN API (Port 8080)

### Job Management
```
POST   /api/v1/jobs/upload                    → Upload PDF/DOCX Job-Dateien
POST   /api/v1/jobs/scrape                    → Web-Scraping (mit renderJs=true für JS-Sites)
POST   /api/v1/jobs/batch-analyze             → Batch-Analyse lokaler Dateien
GET    /api/v1/jobs                           → Alle analysierten Jobs abrufen
```

### Admin & Sync
```
POST   /api/v1/jobs/admin/sync-python-knowledge    → Knowledge von Python synchronisieren
GET    /api/v1/jobs/admin/system-health            → System-Status prüfen
DELETE /api/v1/jobs/admin/clear-all-data           → ⚠️ ALLE Daten löschen
```

### Reports & Analytics
```
GET    /api/v1/jobs/reports/dashboard-metrics      → Job-Statistiken (top_n=10)
GET    /api/v1/jobs/reports/competence-trends      → Top Kompetenzen (limit=5)
GET    /api/v1/jobs/reports/export.csv             → CSV-Export
GET    /api/v1/jobs/reports/export.pdf             → PDF-Export
```

### Rule Management (Domänen-Mappings)
```
GET    /api/v1/rules/blacklist                     → Blacklist (generische Begriffe)
GET    /api/v1/rules/role-mappings                 → Rollen-Mappings
GET    /api/v1/rules/industry-mappings             → Branchen-Mappings
GET    /api/v1/rules/esco-full                     → Vollständige ESCO-Wissensbasis
GET    /api/v1/rules/stats                         → Regelstatistiken
```

### Discovery (Neuentdeckung von Kompetenzen)
```
GET    /api/discovery/candidates                   → Neue Kompetenzkandidaten
GET    /api/discovery/approved                     → Approuvierte Kompetenzen
GET    /api/discovery/ignore                       → Ignorierte Begriffe
POST   /api/discovery/approve                      → Kompetenz genehmigen
POST   /api/discovery/reject                       → Kompetenz ablehnen
```

### Service Links
```
GET    /api/links                                  → Alle Service-Links
GET    /api/v1/test-python                        → Python-Verbindung testen
GET    /test-python                                → (Alias für oben)
```

### System Health
```
GET    /actuator/health                            → Spring Boot Health-Check
```

---

## 🐍 PYTHON BACKEND (Port 8000)

### Job Analysis
```
POST   /analyse/file                               → Lokale Datei analysieren
POST   /analyse/scrape-url                         → URL scrapen + analysieren
POST   /batch-process                              → Alle lokalen Jobs verarbeiten
```

### Knowledge Management
```
GET    /system/status                              → Python-System-Status
POST   /internal/admin/refresh-knowledge           → Knowledge-Base neu laden
```

### Reports
```
GET    /reports/dashboard-metrics                  → Dashboard-Metriken
GET    /reports/export-metrics                     → Metriken-Export
```

### FastAPI Standard
```
GET    /docs                                       → Swagger UI (FastAPI)
GET    /openapi.json                               → OpenAPI-Schema
GET    /redoc                                      → ReDoc-Dokumentation
```

---

## 📊 Request/Response Examples

### Example 1: Web-Scraping mit JavaScript-Rendering
```bash
curl -X POST http://localhost:8080/api/v1/jobs/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.xing.com/jobs/berlin-senior-uiux-designer"
  }?renderJs=true'
```

### Example 2: Batch-Verarbeitung
```bash
curl -X POST http://localhost:8000/batch-process
# Verarbeitet alle PDFs/DOCXs in python-backend/data/jobs/
```

### Example 3: Dashboard-Metriken
```bash
curl http://localhost:8080/api/v1/jobs/reports/dashboard-metrics?top_n=15 | jq '.'
```

### Example 4: System-Status
```bash
curl http://localhost:8080/actuator/health | jq '.'
curl http://localhost:8000/system/status | jq '.'
```

---

## 🔐 WICHTIGE ENDPUNKTE FÜR ENTWICKLUNG

| Endpoint | Zweck | Häufig genutzt |
|----------|-------|----------------|
| `/api/v1/jobs` | Alle Jobs abrufen | ⭐⭐⭐ |
| `/api/v1/jobs/reports/dashboard-metrics` | Dashboard-Daten | ⭐⭐⭐ |
| `/api/v1/jobs/scrape` | URL-Scraping | ⭐⭐ |
| `/batch-process` | Batch-Import | ⭐⭐ |
| `/api/v1/rules/esco-full` | ESCO-Wissensbasis | ⭐ |
| `/api/discovery/candidates` | Neue Kompetenzen | ⭐ |

---

## 🛠️ LOCAL TESTING

### Alles starten
```bash
docker-compose up -d
sleep 15
```

### Health prüfen
```bash
curl http://localhost:8080/actuator/health
curl http://localhost:8000/system/status
```

### Schneller Test: 3 URLs scrapen
```bash
curl -X POST http://localhost:8080/api/v1/jobs/scrape \
  -H "Content-Type: application/json" \
  -d '{"url":"https://xing.com/jobs/..."}?renderJs=true'
```

---

## 📝 NOTES

- **Swagger UI**: `http://localhost:8080/swagger-ui.html`
- **Python FastAPI Docs**: `http://localhost:8000/docs`
- **Jobs-Verzeichnis**: `python-backend/data/jobs/` (für lokale Dateien)
- **Exports**: `python-backend/data/exports/batch_results/` (JSON-Ergebnisse)
- **Fallback-Regeln**: `data/fallback_rules/` (Blacklist, Mappings)

---

**Zuletzt aktualisiert:** 2025-12-27 (Automatisch generiert)
