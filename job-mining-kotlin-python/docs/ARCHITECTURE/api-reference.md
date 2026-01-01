# API-Referenz - HTTP Endpoints

**Base URL:** `http://localhost:8080` (Kotlin API) oder `http://localhost:8000` (Python)

[← Zurück zu Architecture Index](./index.md)

---

## 📋 Inhalt

1. [Job-Analyse Endpoints](#job-analyse)
2. [Discovery Endpoints](#discovery)
3. [System Endpoints](#system)
4. [Admin Endpoints](#admin)
5. [Response Codes](#response-codes)

---

## Job-Analyse

### POST `/api/v1/jobs/scrape`
**Server:** Kotlin API (8080)

Scrapt eine Website und analysiert den Content.

**Request:**
```json
{
  "url": "https://jobs.softgarden.de/...",
  "renderJs": true
}
```

**Parameters:**
- `url` (string, required) - Ziel-URL
- `renderJs` (boolean, optional) - Mit Playwright JS-Rendering? Default: false

**Response (200):**
```json
{
  "id": 123,
  "sourceUrl": "https://...",
  "rawText": "Gesucht: Developer...",
  "jobTitle": "Senior Developer",
  "jobRole": "IT",
  "organization": "Acme GmbH",
  "competences": [
    {
      "id": 1,
      "originalTerm": "Java",
      "escoLabel": "Java Programming",
      "escoUri": "https://data.europa.eu/esco/skill/...",
      "confidenceScore": 0.95,
      "level": 4,
      "isDigital": true,
      "isDiscovery": false
    }
  ],
  "createdAt": "2025-12-28T10:30:00"
}
```

**Error (400):**
```json
{
  "error": "Diese Domain erfordert JS-Rendering. Setze render_js=true"
}
```

**Error (500):**
```json
{
  "error": "Python Backend ist offline"
}
```

---

### POST `/api/v1/jobs` (Upload)
**Server:** Kotlin API (8080)

Hochladen und Analyse von PDF/DOCX Datei.

**Request:** Multipart/Form-Data
```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="jobposting.pdf"
Content-Type: application/pdf

[Binary PDF Content]
------WebKitFormBoundary--
```

**Response (200):** Wie POST `/api/v1/jobs/scrape`

**cURL Beispiel:**
```bash
curl -X POST http://localhost:8080/api/v1/jobs \
  -F "file=@jobposting.pdf"
```

---

### GET `/api/v1/jobs/{id}`
**Server:** Kotlin API (8080)

Job-Details mit allen Competences abrufen.

**Parameters:**
- `id` (integer, path, required) - Job ID

**Response (200):**
```json
{
  "id": 123,
  "sourceUrl": "https://...",
  "filename": "jobposting.pdf",
  "rawText": "...",
  "jobTitle": "Senior Developer",
  "competences": [...]
}
```

**Error (404):**
```json
{
  "error": "Job mit ID 123 nicht gefunden"
}
```

---

### POST `/api/v1/jobs/batch-process`
**Server:** Kotlin API (8080)

Mehrere Jobs parallel verarbeiten.

**Request:**
```json
{
  "jobIds": [1, 2, 3],
  "urls": ["url1", "url2"],
  "fast_mode": false
}
```

**Parameters:**
- `jobIds` (array, optional) - Array von Job-IDs
- `urls` (array, optional) - Array von URLs
- `fast_mode` (boolean, optional) - Schnelle NLP (4000 chars)? Default: false

**Response (200):**
```json
{
  "total": 3,
  "successful": 2,
  "failed": 1,
  "results": [
    {"job_id": 1, "status": "success"},
    {"job_id": 2, "status": "success"},
    {"job_id": 3, "status": "error", "error": "Timeout"}
  ],
  "progress": "completed"
}
```

---

### POST `/batch-analyze` (Alias)
**Server:** Kotlin API (8080)

Alias-Route für Batch-Analyse (gleich wie `/api/v1/jobs/batch-process`).

---

### POST `/batch-process` (Alias)
**Server:** Kotlin API (8080)

Alias-Route für Batch-Analyse (gleich wie `/api/v1/jobs/batch-process`).

---

## Discovery

### GET `/api/v1/discovery/candidates`
**Server:** Kotlin API (8080)

Neue/ungekannte Skills auflisten.

**Response (200):**
```json
[
  {
    "id": 1,
    "skillTerm": "Cloud Architecture",
    "count": 5,
    "firstSeen": "2025-12-27T08:00:00"
  },
  {
    "id": 2,
    "skillTerm": "Kubernetes",
    "count": 3,
    "firstSeen": "2025-12-28T10:00:00"
  }
]
```

---

### GET `/api/v1/discovery/approved`
**Server:** Kotlin API (8080)

Genehmigte Skills auflisten.

**Response (200):**
```json
{
  "java": 10,
  "python": 8,
  "cloud-architecture": 5
}
```

---

### POST `/api/v1/discovery/approve`
**Server:** Kotlin API (8080)

Skill genehmigen und zu ESCO-Daten verknüpfen.

**Request:**
```json
{
  "skillId": 1,
  "escoUri": "https://data.europa.eu/esco/skill/..."
}
```

**Response (200):**
```json
{
  "status": "approved",
  "skillId": 1,
  "escoUri": "https://data.europa.eu/esco/skill/..."
}
```

---

### DELETE `/api/v1/discovery/{skillId}`
**Server:** Kotlin API (8080)

Skill ignorieren (Blacklist).

**Parameters:**
- `skillId` (integer, path, required)

**Response (200):**
```json
{
  "status": "deleted",
  "skillId": 1
}
```

---

### POST `/discovery/candidates`
**Server:** Python API (8000)

Skills aus Discovery in Candidate hinzufügen.

**Request:**
```json
{
  "skill_term": "Cloud Architecture",
  "count": 1
}
```

---

### GET `/discovery/approved`
**Server:** Python API (8000)

Genehmigt Skills aus Python-DB abrufen.

**Response (200):**
```json
{
  "java": 10,
  "python": 8
}
```

---

### POST `/discovery/ignored`
**Server:** Python API (8000)

Skill in Ignore-Liste hinzufügen.

**Request:**
```json
{
  "skill_id": 123
}
```

---

## System

### GET `/api/v1/system/status`
**Server:** Kotlin API (8080)

System-Health-Check (Liveness Probe).

**Response (200):**
```json
{
  "status": "UP",
  "service": "kotlin-api",
  "timestamp": "2025-12-28T10:30:00",
  "version": "2.3.0",
  "database": "connected"
}
```

---

### GET `/health`
**Server:** Python API (8000)

Python-Backend Health-Check.

**Response (200):**
```json
{
  "status": "healthy",
  "python": "3.11",
  "spacy_model": "loaded",
  "playwright": "available"
}
```

---

### GET `/system/status`
**Server:** Python API (8000)

Detaillierter System-Status.

**Response (200):**
```json
{
  "status": "UP",
  "service": "python-backend",
  "timestamp": "2025-12-28T10:30:00",
  "version": "0.8.0",
  "modules": {
    "spacy": "✅",
    "playwright": "✅",
    "esco_data": "✅"
  }
}
```

---

## Admin

### POST `/internal/admin/install-playwright`
**Server:** Python API (8000)

Playwright Browser installieren (mit Fallback).

**Response (200):**
```json
{
  "status": "installed",
  "method": "with-deps"
}
```

**Mögliche Methods:**
- `with-deps` - Mit allen Dependencies
- `with-fonts` - Mit Font-Installation
- `plain` - Nur Chromium (Fallback)

---

## Response Codes

| Code | Bedeutung | Beispiel |
|------|-----------|----------|
| **200** | OK | Request erfolgreich |
| **400** | Bad Request | Ungültige Parameter, JS-Guard aktiviert |
| **404** | Not Found | Resource nicht gefunden |
| **500** | Internal Error | Python-Backend offline, Timeout |
| **503** | Service Unavailable | Datenbank offline |

---

## cURL Beispiele

### Scrape + Analyze
```bash
curl -X POST http://localhost:8080/api/v1/jobs/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://jobs.softgarden.de/...",
    "renderJs": true
  }'
```

### PDF Upload
```bash
curl -X POST http://localhost:8080/api/v1/jobs \
  -F "file=@jobposting.pdf"
```

### Batch Process
```bash
curl -X POST http://localhost:8080/api/v1/jobs/batch-process \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["url1", "url2", "url3"],
    "fast_mode": true
  }'
```

### System Status
```bash
curl http://localhost:8080/api/v1/system/status
```

### Discovery Candidates
```bash
curl http://localhost:8080/api/v1/discovery/candidates
```

### Approve Skill
```bash
curl -X POST http://localhost:8080/api/v1/discovery/approve \
  -H "Content-Type: application/json" \
  -d '{
    "skillId": 1,
    "escoUri": "https://data.europa.eu/esco/skill/..."
  }'
```

---

[← Zurück zu Architecture Index](./index.md)
**Letzte Aktualisierung:** 2025-12-28
