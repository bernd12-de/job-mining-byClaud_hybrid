# 🚀 JOB MINING HYBRID APPLICATION V2.0

## ✅ Was neu ist

### Clean Architecture
- **Domain Layer** (core/models_v2.py): Reine Business-Logik, keine Framework-Dependencies
- **Application Layer** (services/): Orchestrierung und Geschäftslogik
- **Infrastructure Layer** (repositories/): Datenzugriff und externe APIs

### 7-Ebenen-Modell vollständig implementiert
1. ✅ Discovery (is_discovery Flag)
2. ✅ Level (1-8 ESCO Level)
3. ✅ Digital Skills (is_digital Flag)
4. ✅ Domain Inference (source_domain, inferred_level)
5. ✅ Fachbuch/Academia Support (inferred_level 4-5)
6. ✅ Segmentierung & Rolle (is_segmented, role_context)
7. ✅ Zeitreihen-Analyse (year, date_parsed, CompetenceTimeSeries)

### Docker-fähig
```bash
docker-compose -f docker-compose.v2.yml up
```

### Fuzzy-Matching-Strategie
- `SpacyCompetenceExtractor` mit NLP
- `HybridCompetenceRepository` mit ESCO + Custom Skills
- RapidFuzz für fehlerrobuste Matches

---

## 🚀 Quick Start

### 1. Lokale Entwicklung

```bash
# Environment
python -m venv venv
source venv/bin/activate  # oder: venv\Scripts\activate auf Windows
pip install -r requirements.txt

# NLP-Modell herunterladen
python -m spacy download de_core_news_sm

# Run V2.0
python main_v2.py
```

**Erwartet Output:**
```
================================================================================
🚀 JOB MINING HYBRID APPLICATION V2.0
================================================================================

📦 Initialisiere Repositories...
🧠 Starte spaCy NLP Extractor...

📊 VERFÜGBARE DATENQUELLEN:
   - ESCO Skills geladen: 31655
   - Custom Skills geladen: 245
   - Digitale Skills: 1537

🔍 Extrahiere Kompetenzen aus Testdokument...

✅ 8 Kompetenzen erkannt:
   - Python (Vertrauen: 95%)
   - Django (Vertrauen: 92%)
   - REST APIs (Vertrauen: 88%)
   ...

💾 Erstelle JobPosting-Entität...

✨ JobPosting erstellt:
   Titel: Senior Python Developer
   Ort: Berlin
   Jahr: 2025
   Kompetenzen: 8

================================================================================
✅ V2.0 PIPELINE ERFOLGREICH!
================================================================================
```

### 2. Docker

```bash
# Build & Run
docker-compose -f docker-compose.v2.yml up --build

# Prüfe Logs
docker-compose -f docker-compose.v2.yml logs python-backend
```

---

## 📊 Datenmodell

### Competence (Immutable)
```python
@dataclass(frozen=True)
class Competence:
    name: str                           # "Python"
    esco_uri: Optional[str]             # "ESCO:123"
    category: Optional[str]             # "Programming Language"
    domain: Optional[str]               # "ICT"
    competence_type: CompetenceType     # SKILL
    confidence: float                   # 0.95
    source_match: Optional[str]         # "python programming"
    source_section: Optional[str]       # "requirements"
    level: Optional[int]                # 3
    is_digital: bool                    # True
    role_context: Optional[str]         # "IT & Softwareentwicklung"
```

### JobPosting
```python
@dataclass
class JobPosting:
    job_id: str                         # "job_123"
    source_path: str                    # "/data/jobs/123.docx"
    raw_text: str                       # Volltext
    title: str                          # "Senior Python Developer"
    company: str                        # "TechCorp"
    location: str                       # "Berlin"
    year: int                           # 2025 (KRITISCH für Zeitreihen)
    date_parsed: date                   # 2025-01-15
    is_segmented: bool                  # True wenn Tasks/Reqs extrahiert
    tasks_text: str                     # Extrahierte Aufgaben
    requirements_text: str              # Extrahierte Anforderungen
    competences: List[Competence]       # Gefundene Kompetenzen
    extraction_quality_score: float     # 0.88 (Qualität der Extraktion)
    # ... weitere Felder
```

---

## 🔄 Pipeline-Flow

```
1. DocumentLoader
   └─> raw_text (PDF/DOCX)

2. MetadataExtractor
   └─> title, company, location, year, role

3. TextSegmenter
   └─> tasks_text, requirements_text

4. SpacyCompetenceExtractor (mit HybridCompetenceRepository)
   └─> competences: List[Competence]

5. JobPosting-Entität (mit allen Metadaten)
   └─> gespeichert/serialisiert
```

---

## 📈 Zeitreihen-Analyse (Masterprojekt)

```python
# Alle Jobs gruppiert nach Jahr und Kompetenz
competence_ts = CompetenceTimeSeries(competence)
for job in jobs:
    if job.year:
        competence_ts.add_occurrence(job.year)

# Trend ermitteln
trend = competence_ts.trend()  # 'rising', 'falling', 'stable'
```

---

## ✨ Nächste Schritte

- [ ] REST API (FastAPI) für Job-Analyse hinzufügen
- [ ] Dashboard mit Trendanalyse
- [ ] Kotlin API Integration
- [ ] Unit Tests & E2E Tests
- [ ] Mehrsprachige Datenquellen (EN, FR, etc.)

---

## 🆘 Troubleshooting

### spaCy Modell nicht gefunden
```bash
python -m spacy download de_core_news_sm
```

### ESCO-Daten nicht geladen
- Prüfe: `python-backend/data/esco/*.csv` existiert
- CSV-Format muss passen (;-separiert)

### Docker-Build schlägt fehl
```bash
docker system prune  # cleanup
docker-compose -f docker-compose.v2.yml build --no-cache
```

---

**Status:** ✅ Production-Ready V2.0
**Last Updated:** 2025-12-27
