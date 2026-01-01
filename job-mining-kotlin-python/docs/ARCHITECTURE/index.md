# Job Mining System - Architektur-Dokumentation

> **Systemübersicht für Entwickler:** Detaillierte technische Dokumentation aller Komponenten, Module, Methoden und deren Zusammenspiel.

## 📋 Inhaltsverzeichnis

### Komponenten
1. [Kotlin API](#kotlin-api) - Spring Boot Microservice
2. [Python Backend](#python-backend) - FastAPI mit NLP & Web Scraping
3. [PostgreSQL Datenbank](#datenbank) - Persistente Datenspeicherung
4. [Streamlit Dashboard](#streamlit) - Discovery Management UI

### Technische Dokumentation
- [Kotlin API - Detailliert](./kotlin-api.md) - Alle Packages, Klassen, Methoden
- [Python Backend - Detailliert](./python-backend.md) - Alle Module, Funktionen
- [Datenbank-Schema](./database.md) - Tabellen, Relationen, Indices
- [API-Referenz](./api-reference.md) - HTTP Endpoints (GET/POST/DELETE)
- [Datenfluss](./dataflow.md) - Wie Daten durch das System fließen
- [Frameworks & Tech-Stack](./frameworks.md) - Abhängigkeiten, Versionen, Konfiguration

---

## System-Übersicht

### Kotlin API
**Port:** 8080 | **Framework:** Spring Boot 3.x | **Sprache:** Kotlin

**Verantwortung:**
- HTTP REST API für Job-Verarbeitung
- Datenbankzugriff (PostgreSQL)
- Business-Logik für Job Mining
- Integration mit Python NLP-Backend
- Discovery-Management (Approve/Ignore Skills)
- Health-Checks & System-Status

**Hauptkomponenten:**
- **Controllers** (presentation/) - HTTP Request Handling
- **Services** - Business-Logik
- **Repository** - DB-Zugriff (Exposed)
- **Domain Models** - Datenstrukturen (JobPosting, Competence, EscoSkill)
- **Bridges** - Python-Integration

**Wichtigste Klassen:**
- `JobController` - Job-Verarbeitung (POST, GET, BATCH)
- `SystemStatusController` - Health-Check Endpoint
- `DiscoveryController` - Skill-Verwaltung
- `JobMiningService` - Zentrale Business-Logik
- `PythonBridge` - HTTP-Calls zum Python-Backend

---

### Python Backend
**Port:** 8000 | **Framework:** FastAPI | **Sprache:** Python 3.11+

**Verantwortung:**
- NLP-Analyse (spaCy) - Skill-Extraktion
- Web Scraping (Requests, Playwright) - Job-Seiten laden
- Batch-Verarbeitung - Mehrere Jobs gleichzeitig
- ESCO-Daten Matching - Skill-zu-ESCO-Mapping
- Discovery Logging - Neue Skills tracken

**Hauptkomponenten:**
- **API Endpoints** (main.py) - FastAPI Routes
- **Core** (app/core/) - Datenbereinigung, Konstanten
- **Application** - Geschäftslogik (Services, Factories)
- **Infrastructure** - Externe Kommunikation (Scraper, DB, NLP)
- **Extractor** - Text-Processing, Competence-Extraktion
- **Domain** - Datenmodelle (Pydantic)

**Wichtigste Module:**
- `main.py` - FastAPI App, alle Endpoints
- `competence_service.py` - Skill-Analysen
- `esco_service.py` - ESCO-Daten Integration
- `web_scraper.py` - HTML Scraping (Requests + Fallback)
- `js_scraper.py` - Async Playwright für JS-Heavy Sites
- `spacy_competence_extractor.py` - NLP Skill-Extraktion
- `batch_runner.py` - Parallele Job-Verarbeitung

---

### PostgreSQL Datenbank
**Port:** 5432 | **Version:** 14+

**Zentrale Tabellen:**
- `job_postings` - Job-Anzeigen mit Metadaten
- `competences` - Extrahierte Skills pro Job
- `esco_skills` - ESCO-Skill-Mappings
- `discovery_candidates` - Neue/ungekannte Skills
- `discovery_approved` - Vom User freigegebene Skills
- `domain_rules` - Custom Parsing-Regeln
- `audit_log` - Änderungshistorie

[Detailliertes Schema →](./database.md)

---

### Streamlit Dashboard
**Port:** 8501 | **Purpose:** Discovery Management UI

**Features:**
- Kandidaten-Skills ansehen
- Skills approve/reject
- Metriken anzeigen
- Datenbank-Status

[Siehe auch: DASHBOARD_GUIDE.md](../DASHBOARD_GUIDE.md)

---

## 🔄 Request-Flow (Beispiel: Job analysieren)

```
1. Client POST /api/v1/jobs (PDF/DOCX Upload)
   ↓
2. Kotlin: JobController.uploadJob()
   ↓
3. Kotlin: JobMiningService.processJobAd()
   ↓
4. Kotlin: PythonBridge.analyzeJob() → Python-Backend
   ↓
5. Python: scrape_and_analyze_url() oder analyze_pdf()
   ↓
6. Python: WebScraper / pdf_parser
   ↓
7. Python: spacy_competence_extractor.extract_competences()
   ↓
8. Python: esco_service.match_to_esco()
   ↓
9. Python: Return AnalysisResult (Skills + Metadata)
   ↓
10. Kotlin: JobMiningService.saveJobPosting() → DB
    ↓
11. Kotlin: Return JobDTO to Client
```

---

## 📦 Dependencies & Versions

### Kotlin/JVM
- **Spring Boot:** 3.2.0
- **Kotlin:** 2.2.21
- **Exposed:** 0.41.1 (ORM)
- **Jackson:** 2.15.2 (JSON)
- **JUnit 5:** For Testing

### Python
- **FastAPI:** 0.104.1
- **spaCy:** 3.7.2 (NLP)
- **Playwright:** 1.40+ (Browser Automation)
- **Requests:** 2.31+ (HTTP)
- **Pydantic:** 2.5+ (Data Validation)
- **SQLAlchemy:** For DB Access

[Vollständiger Tech-Stack →](./frameworks.md)

---

## 🔐 Wichtige Konstanten & Konfiguration

### Environment Variables
```bash
# Python Backend
SPACY_TEXT_LIMIT=4000              # Max chars für NLP-Analyse
PLAYWRIGHT_AUTO_INSTALL=true       # Browser auto-install
BATCH_PARALLELISM=3                # Parallel Jobs
REQUEST_TIMEOUT=6                  # HTTP Timeout (sec)
MAX_HTML_BYTES=1048576            # HTML Size Limit (1MB)

# Kotlin API
SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/job_mining
PYTHON_BACKEND_URL=http://python-backend:8000
```

### Performance Caps (WebScraper)
- **REQUEST_TIMEOUT:** 3-6 Sekunden pro Request
- **MAX_HTML_BYTES:** 1 MB HTML-Größe
- **MAX_TOTAL_MS:** 8000 ms für gesamten Scrape
- **PLAYWRIGHT_TIMEOUT:** 40 Sekunden für Rendering

---

## 🎯 Nächste Schritte

Detaillierte Dokumentation für jede Komponente:

1. **[Kotlin API Details](./kotlin-api.md)** - Alle 38 Kotlin-Dateien mit Klassen, Methoden, Signaturen
2. **[Python Backend Details](./python-backend.md)** - Alle 50+ Python-Module mit Funktionen, Parametern
3. **[API-Referenz](./api-reference.md)** - Alle HTTP-Endpoints mit Request/Response
4. **[Datenfluss](./dataflow.md)** - Visuelle Übersicht der Datenströme
5. **[Datenbank](./database.md)** - Schema, Relationships, Indices

---

**Letzte Aktualisierung:** 2025-12-28
**Aktuelle Version:** 0.8.0-beta
**Branch:** backup/broken-code-25-12-25
