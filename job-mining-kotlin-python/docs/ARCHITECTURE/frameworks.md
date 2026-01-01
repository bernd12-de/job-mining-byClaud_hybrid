# Frameworks & Tech-Stack

[← Zurück zu Architecture Index](./index.md)

---

## 📦 Kotlin/JVM Stack

### Spring Boot 3.x
```
Framework: Spring Boot 3.2.0
Language: Kotlin 2.2.21
JDK: Java 17 (OpenJDK)
Build Tool: Gradle 8.x
```

**Abhängigkeiten:**
```gradle
dependencies {
    // Spring Boot
    implementation 'org.springframework.boot:spring-boot-starter-web:3.2.0'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa:3.2.0'
    
    // Kotlin
    implementation 'org.jetbrains.kotlin:kotlin-stdlib:2.2.21'
    implementation 'org.jetbrains.kotlin:kotlin-reflect:2.2.21'
    
    // ORM (Exposed)
    implementation 'org.jetbrains.exposed:exposed-core:0.41.1'
    implementation 'org.jetbrains.exposed:exposed-dao:0.41.1'
    implementation 'org.jetbrains.exposed:exposed-kotlin-datetime:0.41.1'
    
    // Database
    implementation 'org.postgresql:postgresql:42.6.0'
    
    // JSON
    implementation 'com.fasterxml.jackson.core:jackson-databind:2.15.2'
    implementation 'com.fasterxml.jackson.datatype:jackson-datatype-jsr310:2.15.2'
    
    // HTTP Client
    implementation 'org.springframework.boot:spring-boot-starter-webflux:3.2.0'
    implementation 'io.ktor:ktor-client-core:2.3.0'
    
    // Swagger / OpenAPI
    implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:2.0.2'
    
    // Logging
    implementation 'org.springframework.boot:spring-boot-starter-logging:3.2.0'
    implementation 'org.slf4j:slf4j-api:2.0.5'
    
    // Testing
    testImplementation 'org.springframework.boot:spring-boot-starter-test:3.2.0'
    testImplementation 'org.junit.jupiter:junit-jupiter:5.9.2'
    testImplementation 'io.mockk:mockk:1.13.4'
}
```

### Exposed ORM
**Alternative zu Hibernate/JPA**

```kotlin
// Definition
object JobPostingsTable : Table() {
    val id = long("id").autoIncrement()
    val sourceUrl = varchar("source_url", 1000).nullable()
    val rawText = text("raw_text")
    val rawTextHash = varchar("raw_text_hash", 64)
    
    override val primaryKey = PrimaryKey(id)
}

// Usage
transaction {
    JobPostingsTable.insert {
        it[sourceUrl] = "https://..."
        it[rawText] = "..."
        it[rawTextHash] = "abc123"
    }
}
```

### Jackson (JSON Serialization)
```kotlin
val objectMapper = ObjectMapper()
    .registerModule(JavaTimeModule())
    .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
    .setDefaultPrettyPrinter(DefaultPrettyPrinter())

// Serialization
val json = objectMapper.writeValueAsString(jobPosting)

// Deserialization
val dto = objectMapper.readValue(json, JobDTO::class.java)
```

### Spring Boot Annotations
```kotlin
@SpringBootApplication      // Main App
@Configuration              // Config-Klasse
@Service                    // Business-Service
@Repository                 // DB-Zugriff
@RestController             // HTTP Controller
@RequestMapping("/path")    // Route Base
@GetMapping, @PostMapping   // HTTP Verbs
@Autowired                  // Dependency Injection
@Transactional              // DB Transaction
```

---

## 📦 Python Stack

### FastAPI
```
Framework: FastAPI 0.104.1
Server: Uvicorn 0.24.0
Python: 3.11+
Package Manager: pip
```

**Installation:**
```bash
pip install fastapi uvicorn python-multipart
```

**Beispiel:**
```python
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

app = FastAPI(title="Job Mining Backend", version="0.8.0")

@app.post("/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    content = await file.read()
    return {"status": "analyzed"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Server starten:
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Pydantic (Data Validation)
```python
from pydantic import BaseModel, Field

class CompetenceDTO(BaseModel):
    originalTerm: str = Field(..., min_length=1)
    escoLabel: Optional[str] = None
    confidenceScore: float = Field(0.0, ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "originalTerm": "Java",
                "escoLabel": "Java Programming",
                "confidenceScore": 0.95
            }
        }

# Validierung automatisch
data = CompetenceDTO(originalTerm="Python", confidenceScore=0.8)
```

### spaCy (NLP)
```
Library: spaCy 3.7.2
Model: de_core_news_sm (German)
```

**Installation & Usage:**
```bash
pip install spacy

# Download Model
python -m spacy download de_core_news_sm
```

```python
import spacy

nlp = spacy.load("de_core_news_sm")
doc = nlp("Java und Python sind Programming-Sprachen")

# Named Entity Recognition
for ent in doc.ents:
    print(f"{ent.text} ({ent.label_})")

# Tokenization
for token in doc:
    print(f"{token.text}: {token.pos_}")
```

**Konfiguration:**
```bash
# Limit für große Texte
export SPACY_TEXT_LIMIT=4000
```

### Playwright (Browser Automation)
```
Library: Playwright 1.40+
Browsers: Chromium, Firefox, WebKit
Mode: Async (for FastAPI)
```

**Installation:**
```bash
pip install playwright
playwright install chromium  # oder: --with-deps
```

**Async Usage:**
```python
from playwright.async_api import async_playwright

async def scrape_with_javascript(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(url, wait_until="networkidle")
        content = await page.content()
        
        await browser.close()
        return content
```

**Features:**
- Headless browsing
- JS rendering
- Cookie handling
- Screenshot capability
- Network interception

### Requests (HTTP Client)
```
Library: Requests 2.31+
```

**Usage:**
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Retry strategy
session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# GET
response = session.get("https://...", timeout=6)

# POST
response = session.post("https://...", json={"key": "value"})
```

### BeautifulSoup4 (HTML Parsing)
```
Library: BeautifulSoup4 4.12.2
```

```python
from bs4 import BeautifulSoup

html = "<html>...</html>"
soup = BeautifulSoup(html, "html.parser")

# CSS Selectors
job_title = soup.select_one(".job-title")

# Tags
for p in soup.find_all("p"):
    print(p.text)

# Attributes
link = soup.find("a")
href = link.get("href")
```

### SQLAlchemy (ORM)
```
Library: SQLAlchemy 2.0.23
```

**Basic Model:**
```python
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

class JobPosting(Base):
    __tablename__ = "job_postings"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(String(5000))

# Connection
engine = create_engine("postgresql://user:pass@localhost/dbname")
with Session(engine) as session:
    jobs = session.query(JobPosting).filter_by(title="Developer").all()
```

### Asyncio (Async/Await)
```
Python built-in async library
```

```python
import asyncio

async def fetch_url(url):
    # Simulated async I/O
    await asyncio.sleep(1)
    return f"Data from {url}"

async def main():
    tasks = [
        fetch_url("url1"),
        fetch_url("url2"),
        fetch_url("url3")
    ]
    results = await asyncio.gather(*tasks)
    return results

# Run
asyncio.run(main())
```

---

## 🗄️ Database

### PostgreSQL
```
DBMS: PostgreSQL 14+
Port: 5432
Driver: psycopg2 (Python), PostgreSQL Driver (Kotlin)
```

**Connection String (Kotlin):**
```
jdbc:postgresql://postgres:5432/job_mining
```

**Connection String (Python):**
```
postgresql://postgres:password@postgres:5432/job_mining
```

**Useful Commands:**
```bash
# Connect
psql -h postgres -U postgres -d job_mining

# List tables
\dt

# Describe table
\d job_postings

# Query
SELECT * FROM job_postings LIMIT 10;
```

---

## 🎨 Streamlit (UI)

```
Library: Streamlit 1.28.1
Port: 8501
```

**Dashboard File:** `dashboard_app.py`

**Structure:**
```python
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Job Mining Discovery")

st.title("🔍 Skill Discovery Management")

# Sidebar
with st.sidebar:
    st.header("Settings")
    page = st.radio("Select Page", ["Candidates", "Approved", "Analytics"])

# Main Content
if page == "Candidates":
    candidates = fetch_candidates()
    st.dataframe(candidates)
    
    if st.button("Refresh"):
        st.rerun()

# Run:
# streamlit run dashboard_app.py
```

**Key Functions:**
- `st.title()`, `st.header()`, `st.subheader()` - Headers
- `st.write()` - Output
- `st.dataframe()` - Table display
- `st.button()` - Button
- `st.selectbox()`, `st.multiselect()` - Dropdowns
- `st.slider()`, `st.text_input()` - Input
- `st.session_state` - State management
- `st.container()`, `st.columns()` - Layout

---

## 🔄 Docker & Compose

### docker-compose.yml
```yaml
version: '3.9'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: job_mining
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  kotlin-api:
    build:
      context: ./kotlin-api
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/job_mining
      PYTHON_BACKEND_URL: http://python-backend:8000
    depends_on:
      - postgres
      - python-backend

  python-backend:
    build:
      context: ./python-backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/job_mining
      SPACY_TEXT_LIMIT: 4000
      PLAYWRIGHT_AUTO_INSTALL: "true"
    depends_on:
      - postgres

  streamlit:
    build:
      context: ./python-backend
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    depends_on:
      - python-backend

volumes:
  postgres_data:
```

**Commands:**
```bash
# Start all services
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f python-backend

# Access service
docker-compose exec postgres psql -U postgres -d job_mining
```

---

## 📊 Development Tools

### IDE Setup
- **IntelliJ IDEA** (Kotlin) - mit Kotlin Plugin
- **VSCode** - mit Pylance, Kotlin Extension
- **PyCharm** (Python) - Community Edition

### Debugging
```kotlin
// Kotlin - add breakpoints in IDE
logger.info("Debug: $variable")

@GetMapping("/test")
fun debug(): String {
    println("Debug output")  // Console
    return "ok"
}
```

```python
# Python - add breakpoints
import pdb; pdb.set_trace()

# Or use logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Debug: {variable}")
```

### Testing Frameworks
```
Kotlin: JUnit 5, Mockk, AssertJ
Python: pytest, httpx, pytest-asyncio
```

---

## 🔐 Environment Configuration

**`.env` file (local):**
```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/job_mining
SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/job_mining

# Services
PYTHON_BACKEND_URL=http://localhost:8000
KOTLIN_API_URL=http://localhost:8080

# Performance
SPACY_TEXT_LIMIT=4000
REQUEST_TIMEOUT=6
MAX_HTML_BYTES=1048576

# Features
PLAYWRIGHT_AUTO_INSTALL=true
BATCH_PARALLELISM=3
```

---

## 📋 Version Pinning

**Kotlin (gradle):**
```gradle
ext {
    kotlinVersion = "2.2.21"
    springBootVersion = "3.2.0"
    javaVersion = "17"
}
```

**Python (requirements.txt):**
```
FastAPI==0.104.1
spacy==3.7.2
playwright==1.40.0
pytest==7.4.3
```

---

[← Zurück zu Architecture Index](./index.md)
**Letzte Aktualisierung:** 2025-12-28
