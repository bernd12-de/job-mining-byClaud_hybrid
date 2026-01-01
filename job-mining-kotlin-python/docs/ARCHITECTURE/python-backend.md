# Python Backend - Detaillierte Dokumentation

**Framework:** FastAPI | **Python:** 3.11+ | **Port:** 8000
**Gesamte Python-Module:** 50+
**Haupteingabedatei:** `main.py`

[← Zurück zu Architecture Index](./index.md)

---

## 📦 Module-Übersicht

```
python-backend/
├── main.py                          # FastAPI Hauptprogramm (Alle Endpoints!)
│
├── app/
│   ├── __init__.py
│   │
│   ├── core/                        # Core-Funktionen & Konstanten
│   │   ├── api_endpoints.py         # API-Handler (scrape_and_analyze_url, etc.)
│   │   ├── constants.py             # Alle Konstanten (Timeouts, Limits)
│   │   ├── normalize.py             # Text-Normalisierung
│   │   ├── skill_filter.py          # Skill-Filtering-Logik
│   │   └── __init__.py
│   │
│   ├── domain/                      # Datenmodelle (Pydantic)
│   │   ├── models.py                # Alle DTOs & Schemas
│   │   └── __init__.py
│   │
│   ├── application/                 # Business-Logik & Orchester
│   │   ├── competence_service.py    # Service für Competence-Operationen
│   │   ├── job_mining_workflow_manager.py  # Batch-Workflow
│   │   ├── factories/
│   │   │   ├── analysis_result_factory.py  # DTO-Konstruktion
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── esco_service.py      # ESCO-Daten Matching (Wichtig!)
│   │   │   ├── organization_service.py
│   │   │   ├── role_service.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   │
│   ├── infrastructure/              # External Integration
│   │   ├── batch/
│   │   │   ├── batch_runner.py      # Parallele Job-Verarbeitung
│   │   │   └── __init__.py
│   │   ├── clients/
│   │   │   ├── kotlin_rule_client.py # HTTP zu Kotlin API
│   │   │   └── __init__.py
│   │   ├── crawling/
│   │   │   ├── web_scraper.py       # HTML Scraping (Requests + Fallback)
│   │   │   └── __init__.py
│   │   ├── data/
│   │   │   ├── esco_data_repository.py  # ESCO-Daten laden
│   │   │   ├── esco_skills.py       # ESCO JSON-Files
│   │   │   └── __init__.py
│   │   ├── extractor/               # Text-Verarbeitung (NLP)
│   │   │   ├── advanced_text_extractor.py
│   │   │   ├── competence_extractor.py
│   │   │   ├── discovery_extractor.py      # Neue Skills tracking
│   │   │   ├── discovery_logger.py
│   │   │   ├── fuzzy_competence_extractor.py
│   │   │   ├── metadata_extractor.py       # Titel, Org, etc.
│   │   │   ├── spacy_competence_extractor.py  # NLP Skill-Extraction
│   │   │   └── __init__.py
│   │   ├── io/
│   │   │   ├── js_scraper.py        # Async Playwright (Wichtig!)
│   │   │   ├── check_paths.py
│   │   │   ├── domain_generator.py
│   │   │   ├── job_directory_processor.py
│   │   │   ├── smart_domain_generator.py
│   │   │   └── __init__.py
│   │   ├── exporter.py              # Export zu CSV/JSON
│   │   ├── job_classifier.py        # Job-Klassifizierung
│   │   ├── reporting.py             # Report-Generierung
│   │   ├── repositories/
│   │   │   ├── hybrid_competence_repository.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   │
│   ├── interfaces/                  # Abstrakte Interfaces
│   │   ├── interfaces.py            # Interface-Definitionen
│   │   ├── repository.py            # Repository-Pattern
│   │   └── __init__.py
│   │
│   ├── api/
│   │   ├── dashboard_api.py         # Streamlit-Integration
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── dashboard_app.py                 # Streamlit UI
└── requirements.txt                 # Dependencies
```

---

## 🎯 Hauptendpoints (main.py)

### 1. Job-Analyse Endpoints

#### POST `/analyze-document`
```python
async def analyze_document(
    file: UploadFile = File(...)
) -> AnalysisResult:
    """
    Analysiert hochgeladene PDF/DOCX
    """
    content = await file.read()
    text = extract_text_from_pdf(content)  # oder DOCX
    
    competences = await competence_service.extract_competences(text)
    metadata = await metadata_extractor.extract(text)
    
    return AnalysisResult(
        rawText=text,
        competences=competences,
        jobTitle=metadata.job_title,
        sourceUrl=None,
        rawTextHash=hash(text)
    )
```

**Request:** Multipart/Form-Data mit File
**Response:** AnalysisResult JSON
**Status:** 200/400/500

---

#### POST `/scrape-and-analyze`
```python
async def scrape_and_analyze_url(
    url: str = Query(...),
    render_js: bool = Query(False)
) -> AnalysisResult:
    """
    Scrapt URL und analysiert Content
    """
    if render_js:
        html = await scrape_with_rendering(url)  # Playwright async
    else:
        html = scraper.scrape(url)               # Requests
    
    text = extract_text_from_html(html)
    competences = await competence_service.extract_competences(text)
    
    return AnalysisResult(...)
```

**Query Parameters:**
- `url` - Ziel-URL
- `render_js` - Boolean, JS-Rendering?

**Response:** AnalysisResult JSON

---

#### POST `/batch-process`
```python
async def batch_process(
    request: BatchRequest  # {job_ids: [1,2,3]} oder {urls: [...]}
) -> BatchResult:
    """
    Verarbeitet mehrere Jobs parallel
    """
    results = await job_mining_workflow_manager.process_batch(
        request.job_ids,
        request.urls,
        max_workers=3  # Parallelism
    )
    return BatchResult(results=results, progress="completed")
```

**Request Body:**
```json
{
  "job_ids": [1, 2, 3],
  "urls": ["url1", "url2"],
  "fast_mode": false
}
```

**Response:** BatchResult mit Progress-Info

---

### 2. Discovery Endpoints (Skill-Management)

#### GET `/discovery/candidates`
```python
async def get_discovery_candidates() -> List[dict]:
    """
    Neue/ungekannte Skills auflisten
    """
    return discovery_repository.get_candidates()
```

**Response:**
```json
[
  {"id": 1, "skill_term": "Cloud Architecture", "count": 5},
  {"id": 2, "skill_term": "Kubernetes", "count": 3}
]
```

---

#### POST `/discovery/approve`
```python
async def approve_discovery_skill(
    request: ApproveRequest  # {skill_id, esco_uri}
) -> dict:
    """
    Markiert Skill als gültig
    """
    discovery_repository.approve(request.skill_id, request.esco_uri)
    return {"status": "approved"}
```

---

#### POST `/discovery/ignored`
```python
async def add_to_ignored(
    request: IgnoreRequest  # {skill_id}
) -> dict:
    """
    Skill ignorieren (Blacklist)
    """
    discovery_repository.ignore(request.skill_id)
    return {"status": "ignored"}
```

---

#### DELETE `/discovery/{skill_id}`
```python
async def delete_discovery_skill(skill_id: int) -> dict:
    """
    Skill aus Discovery löschen
    """
    discovery_repository.delete(skill_id)
    return {"status": "deleted"}
```

---

### 3. Admin Endpoints

#### POST `/internal/admin/install-playwright`
```python
async def install_playwright_admin() -> dict:
    """
    Installiert Playwright Browser (Fallback)
    
    Strategie:
    1. Versuche: playwright install --with-deps
    2. Falls fehlt (Fonts): Install fonts separat
    3. Fallback: playwright install (ohne deps)
    """
    try:
        subprocess.run(["playwright", "install", "--with-deps"], check=True)
        return {"status": "installed", "method": "with-deps"}
    except:
        try:
            subprocess.run(["apt-get", "install", "-y", "fonts-dejavu"], check=True)
            subprocess.run(["playwright", "install"], check=True)
            return {"status": "installed", "method": "with-fonts"}
        except:
            subprocess.run(["playwright", "install"], check=True)
            return {"status": "installed", "method": "plain"}
```

---

### 4. System Endpoints

#### GET `/health`
```python
async def health_check() -> dict:
    """
    Health-Status prüfen
    """
    return {
        "status": "healthy",
        "python": "3.11",
        "spacy_model": "loaded",
        "playwright": "available"
    }
```

---

#### GET `/system/status`
```python
async def system_status() -> dict:
    """
    Detaillierter System-Status
    """
    return {
        "status": "UP",
        "service": "python-backend",
        "timestamp": datetime.now().isoformat(),
        "version": "0.8.0",
        "modules": {
            "spacy": "✅",
            "playwright": "✅",
            "esco_data": "✅"
        }
    }
```

---

---

## 📚 Wichtigste Module & Funktionen

### 1. api_endpoints.py (Core-Handler)
**File:** `app/core/api_endpoints.py`

#### `async def scrape_and_analyze_url(url: str, render_js: bool = False) -> AnalysisResult`
```python
async def scrape_and_analyze_url(url: str, render_js: bool = False):
    """
    Haupt-Endpunkt: Url scrapen + analysieren
    
    Strategie:
    1. JS-Domain Guard: Wenn render_js=false aber Domain braucht JS → 400 Error
    2. Scraping:
       - render_js=true → scrape_with_rendering() [Playwright async]
       - render_js=false → WebScraper().scrape() [Requests]
    3. Text Extraction + Cleanup
    4. Fast-Mode: Text auf 4000 chars trimmen (wenn fast=true)
    5. NLP-Extraktion
    6. ESCO-Matching
    """
    
    # 1. Guard: JS-Heavy Domains
    if not render_js and is_javascript_heavy_domain(url):
        raise HTTPException(
            status_code=400,
            detail="Diese Domain erfordert JS-Rendering. Setze render_js=true"
        )
    
    # 2. Scraping
    if render_js:
        html = await scrape_with_rendering(url)  # Async Playwright
    else:
        scraper = WebScraper()
        html = scraper.scrape(url)
    
    # 3-6. Processing
    text = extract_text_from_html(html)
    if fast_mode:
        text = text[:4000]  # Trim für Performance
    
    competences = await competence_service.extract_competences(text)
    
    return AnalysisResult(...)
```

**Parameters:**
- `url` - Ziel-URL
- `render_js` - Mit Playwright?

**Return:** AnalysisResult DTO

**Wirft:** HTTPException (400 für JS-Guard, 500 bei Fehler)

---

#### `def analyze_document(file_content: bytes, filename: str) -> AnalysisResult`
```python
def analyze_document(file_content: bytes, filename: str):
    """
    PDF/DOCX analysieren
    """
    if filename.endswith('.pdf'):
        text = pdf_parser.extract_text(file_content)
    elif filename.endswith('.docx'):
        text = docx_parser.extract_text(file_content)
    else:
        raise ValueError("Nur PDF/DOCX unterstützt")
    
    competences = competence_service.extract_competences(text)
    return AnalysisResult(rawText=text, competences=competences)
```

---

### 2. esco_service.py (ESCO-Matching)
**File:** `app/application/services/esco_service.py`

#### `def match_competence_to_esco(skill_term: str, context: str = "") -> ESCOMatch`
```python
def match_competence_to_esco(skill_term: str, context: str = ""):
    """
    Matched einen extrahierten Skill zu ESCO-Datensatz
    
    Strategie:
    1. Exact Match in ESCO-DB
    2. Fuzzy Match (Levenshtein, 80%+ similarity)
    3. Context-basiertes Matching (Jobbezeichnung hilft)
    4. Fallback: Markiere als Discovery-Kandidat
    """
    
    # 1. Exact Match
    esco_entry = esco_repository.find_by_label(skill_term)
    if esco_entry:
        return ESCOMatch(
            originalTerm=skill_term,
            escoLabel=esco_entry.label,
            escoUri=esco_entry.uri,
            confidenceScore=1.0,
            isDiscovery=False
        )
    
    # 2. Fuzzy Match
    candidates = esco_repository.fuzzy_search(skill_term)
    if candidates:
        best = max(candidates, key=lambda x: x['similarity'])
        if best['similarity'] >= 0.8:
            return ESCOMatch(
                originalTerm=skill_term,
                escoLabel=best['label'],
                escoUri=best['uri'],
                confidenceScore=best['similarity'],
                isDiscovery=False
            )
    
    # 4. Discovery-Kandidat
    return ESCOMatch(
        originalTerm=skill_term,
        escoLabel=None,
        escoUri=None,
        confidenceScore=0.0,
        isDiscovery=True  # ← Markiere als neu
    )
```

**Return:** ESCOMatch DTO

---

### 3. spacy_competence_extractor.py (NLP)
**File:** `app/infrastructure/extractor/spacy_competence_extractor.py`

#### `async def extract_competences(text: str) -> List[CompetenceDTO]`
```python
async def extract_competences(text: str):
    """
    NLP-basierte Skill-Extraktion mit spaCy
    
    Schritte:
    1. Text laden & spaCy verarbeiten
    2. Named Entity Recognition (NER)
    3. Pattern Matching (z.B. "Java", "Python")
    4. Confidence-Scoring
    5. Deduplication (gleiche Skills kombinieren)
    """
    
    # 1. spaCy Processing
    doc = nlp(text)  # nlp = spacy.load("de_core_news_sm")
    
    competences = []
    
    # 2-3. Entitäten + Patterns
    for token in doc:
        if is_skill_keyword(token.text):
            competences.append(CompetenceDTO(
                originalTerm=token.text,
                confidenceScore=0.8
            ))
    
    # 5. Deduplication
    seen = {}
    for comp in competences:
        key = comp.originalTerm.lower()
        if key not in seen:
            seen[key] = comp
    
    return list(seen.values())
```

**Environment:** `SPACY_TEXT_LIMIT=4000` - Max Text-Größe

---

### 4. js_scraper.py (Async Playwright)
**File:** `app/infrastructure/io/js_scraper.py`

#### `async def scrape_with_rendering(url: str) -> str`
```python
async def scrape_with_rendering(url: str):
    """
    Async Playwright für JS-Heavy Websites
    
    Timeout: 40 Sekunden
    Features:
    - Cookie-Banner Acceptance (OneTrust, German buttons)
    - Portal-spezifische Selektoren (Workday, Softgarden)
    - Headless Mode für Sicherheit
    """
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Timeout
            await asyncio.wait_for(
                page.goto(url, wait_until="networkidle"),
                timeout=40.0
            )
            
            # Cookie-Banner acceptance
            accept_cookies(page)
            
            # Portal-spezifische Selektoren
            if "workday" in url:
                selector = 'div[data-job-title]'
            elif "softgarden" in url:
                selector = 'article.job-posting'
            else:
                selector = 'body'
            
            # Content extrahieren
            content = await page.locator(selector).inner_html()
            
            return content
            
        finally:
            await browser.close()
```

---

### 5. web_scraper.py (Requests + Fallback)
**File:** `app/infrastructure/crawling/web_scraper.py`

#### `def scrape(url: str) -> str`
```python
def scrape(url: str):
    """
    HTML Scraping mit Requests
    
    Performance Caps:
    - REQUEST_TIMEOUT: 3-6 Sekunden
    - MAX_HTML_BYTES: 1 MB
    - MAX_TOTAL_MS: 8000 ms
    
    Fallback auf Playwright wenn nötig
    """
    
    start_time = time.time()
    
    try:
        response = requests.get(
            url,
            timeout=6,
            stream=True  # Streaming für Size-Limit
        )
        
        # Size-Limit Check
        html = b""
        for chunk in response.iter_content(chunk_size=8192):
            html += chunk
            if len(html) > MAX_HTML_BYTES:  # 1 MB
                break
        
        # Timeout-Check
        elapsed_ms = (time.time() - start_time) * 1000
        if elapsed_ms > MAX_TOTAL_MS:  # 8000 ms
            raise TimeoutError(f"Scrape took {elapsed_ms}ms")
        
        return html.decode('utf-8', errors='ignore')
        
    except Exception as e:
        # Fallback: Playwright Install
        try:
            subprocess.run(["playwright", "install", "--with-deps"], check=True)
        except:
            try:
                subprocess.run(["apt-get", "install", "-y", "fonts-dejavu"], check=True)
            except:
                subprocess.run(["playwright", "install"], check=True)
        
        raise
```

**Konstanten:**
```python
REQUEST_TIMEOUT = 6          # Sekunden
MAX_HTML_BYTES = 1048576    # 1 MB
MAX_TOTAL_MS = 8000         # 8 Sekunden
```

---

### 6. batch_runner.py (Parallel)
**File:** `app/infrastructure/batch/batch_runner.py`

#### `async def process_batch(job_ids: List[int]) -> BatchResult`
```python
async def process_batch(job_ids: List[int], max_workers: int = 3):
    """
    Mehrere Jobs parallel verarbeiten
    
    Begrenzt auf max_workers (default 3) für Performance
    """
    
    async def process_single(job_id):
        try:
            result = await competence_service.process_job(job_id)
            return {"job_id": job_id, "status": "success", "result": result}
        except Exception as e:
            return {"job_id": job_id, "status": "error", "error": str(e)}
    
    # Parallel mit Limit
    tasks = [process_single(job_id) for job_id in job_ids]
    results = await asyncio.gather(*tasks)
    
    return BatchResult(
        results=results,
        progress="completed",
        total=len(job_ids),
        successful=len([r for r in results if r['status'] == 'success'])
    )
```

---

## 🔐 DTOs (Pydantic Models)

**File:** `app/domain/models.py`

### AnalysisResult
```python
class AnalysisResult(BaseModel):
    rawText: str
    rawTextHash: str           # MD5 für Idempotenz
    extractedText: Optional[str]
    sourceUrl: Optional[str]   # Falls Web-Scrape
    jobTitle: Optional[str]
    competences: List[CompetenceDTO]
    processingTime: int        # ms
```

### CompetenceDTO
```python
class CompetenceDTO(BaseModel):
    originalTerm: str          # Original aus Text
    escoLabel: Optional[str]
    escoUri: Optional[str]
    confidenceScore: float     # 0.0-1.0
    escoGroupCode: Optional[str]
    isDigital: bool
    isDiscovery: bool          # Neu entdeckt?
    level: Optional[int]       # 2, 4 oder 5
    roleContext: Optional[str]
    sourceDomain: Optional[str]
```

### ESCOMatch
```python
class ESCOMatch(BaseModel):
    originalTerm: str
    escoLabel: Optional[str]
    escoUri: Optional[str]
    confidenceScore: float
    matchType: str  # "exact", "fuzzy", "discovery"
    isDiscovery: bool
```

---

## ⚙️ Wichtige Konstanten

**File:** `app/core/constants.py`

```python
# Performance Caps
REQUEST_TIMEOUT = 6              # Sekunden
MAX_HTML_BYTES = 1048576        # 1 MB
MAX_TOTAL_MS = 8000             # 8 Sekunden
PLAYWRIGHT_TIMEOUT = 40          # 40 Sekunden

# NLP
SPACY_TEXT_LIMIT = 4000         # Max chars
SPACY_MODEL = "de_core_news_sm"

# Batch
BATCH_PARALLELISM = 3           # Max gleichzeitige Jobs
BATCH_MAX_SIZE = 100            # Max Jobs pro Batch

# Confidence
MIN_CONFIDENCE = 0.6            # Min Confidence für Matches
FUZZY_MATCH_THRESHOLD = 0.8     # Min Similarity für Fuzzy

# Domains mit JS-Requirement
JS_REQUIRED_DOMAINS = [
    "workday.com",
    "linkedin.com",
    "indeed.com"
]
```

---

## 🔍 Dependencies (requirements.txt)

```
FastAPI==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
spacy==3.7.2
playwright==1.40.0
requests==2.31.0
beautifulsoup4==4.12.2
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dateutil==2.8.2
streamlit==1.28.1
pytest==7.4.3
```

---

## 🧪 Testing

**Test-Datei:** `test_system.py`

```python
@pytest.mark.asyncio
async def test_analyze_document():
    with open("sample.pdf", "rb") as f:
        result = await api_endpoints.analyze_document(f.read(), "sample.pdf")
    
    assert result.rawText is not None
    assert len(result.competences) > 0

@pytest.mark.asyncio
async def test_scrape_softgarden():
    result = await api_endpoints.scrape_and_analyze_url(
        "https://softgarden.io/...", 
        render_js=True
    )
    assert result.sourceUrl is not None
```

**Bekannte Probleme:**
- 2 Tests schlagen fehl (matcher, industry heuristic)
- 29 von 31 Tests bestanden

---

[← Zurück zu Architecture Index](./index.md)
**Letzte Aktualisierung:** 2025-12-28
