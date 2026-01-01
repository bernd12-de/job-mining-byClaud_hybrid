# Requirements Installation Guide

## 📦 Modulare Installation

Die Dependencies sind jetzt **modular** aufgeteilt, sodass du nur installieren musst, was du wirklich brauchst!

---

## 🎯 Installation-Optionen

### Option 1: **MINIMAL** (Empfohlen zum Testen)

```bash
pip install -r requirements.txt
```

**Enthält:**
- ✅ FastAPI + Streamlit (API + Dashboard)
- ✅ spaCy + RapidFuzz (NLP + Skill-Matching)
- ✅ Pandas + Plotly (Datenverarbeitung + Visualisierung)
- ✅ Web-Scraping (BeautifulSoup, Playwright)
- ✅ PDF/DOCX Parsing (normale Dateien)
- ✅ **Geo-Visualisierung** 🗺️

**Funktioniert für:**
- Dashboard anzeigen
- Normale PDFs/DOCX verarbeiten
- Skill-Extraktion (RapidFuzz)
- Geo-Karte anzeigen
- Web-Scraping

**NICHT enthalten:**
- ❌ Gescannte PDFs (OCR)
- ❌ Semantic Matching (Transformers)
- ❌ PostgreSQL

---

### Option 2: **+ OCR Features**

```bash
pip install -r requirements.txt
pip install -r requirements-ocr.txt
```

**Zusätzlich zu Minimal:**
- ✅ Gescannte PDFs verarbeiten
- ✅ Screenshots extrahieren
- ✅ Image-to-Text Konvertierung

**System-Dependencies (Linux):**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-deu poppler-utils
```

---

### Option 3: **+ ML Features**

```bash
pip install -r requirements.txt
pip install -r requirements-ml.txt
```

**Zusätzlich zu Minimal:**
- ✅ Semantic Similarity (ESCO Dual-Mapping)
- ✅ Transformer Models (MiniLM, MultiLM)
- ✅ Bessere Skill-Matching Accuracy (90% → 95%)

**⚠️ WARNUNG:** Downloads ~500MB ML-Modelle beim ersten Start!

---

### Option 4: **+ PostgreSQL**

```bash
pip install -r requirements.txt
pip install -r requirements-db.txt
```

**Zusätzlich zu Minimal:**
- ✅ PostgreSQL Datenbankunterstützung
- ✅ Persistente Speicherung von Jobs
- ✅ Kompetenz-Tracking

**Voraussetzung:** PostgreSQL Server muss laufen

---

### Option 5: **FULL** (Alles)

```bash
pip install -r requirements-full.txt
```

**Enthält:**
- ✅ Core + OCR + ML + Database
- ✅ Alle Features aktiviert
- ✅ Production-Ready

**System-Dependencies:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-deu poppler-utils
```

---

## 🚀 Quick Start

### Schnellster Start (ohne Dependencies-Probleme):

```bash
# 1. Minimal-Installation
cd python-backend
pip install -r requirements.txt

# 2. spaCy Modell herunterladen
python -m spacy download de_core_news_md

# 3. Dashboard starten
streamlit run dashboard_app.py
```

**Öffne Browser:** http://localhost:8501

✅ **Geo-Karte funktioniert sofort!**

---

## 📊 Feature-Matrix

| Feature | Minimal | +OCR | +ML | +DB | Full |
|---------|---------|------|-----|-----|------|
| **Dashboard** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Geo-Karte** 🗺️ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Normale PDFs** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Gescannte PDFs** | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Skill-Matching (Fuzzy)** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Semantic Matching** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **PostgreSQL** | ❌ | ❌ | ❌ | ✅ | ✅ |

---

## 💡 Empfehlungen

**Für Entwicklung/Testing:**
```bash
pip install -r requirements.txt  # Minimal
```

**Für Production (ohne DB):**
```bash
pip install -r requirements.txt
pip install -r requirements-ocr.txt
pip install -r requirements-ml.txt
```

**Für Production (mit DB):**
```bash
pip install -r requirements-full.txt
```

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'PIL'"
**Lösung:**
```bash
pip install -r requirements-ocr.txt
```

### Problem: "ModuleNotFoundError: No module named 'sentence_transformers'"
**Lösung:**
```bash
pip install -r requirements-ml.txt
```

### Problem: "ModuleNotFoundError: No module named 'psycopg2'"
**Lösung:**
```bash
pip install -r requirements-db.txt
```

### Problem: Tesseract nicht gefunden
**Lösung:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-deu poppler-utils
```

---

## 📝 Hinweise

1. **spaCy Modell** muss IMMER separat installiert werden:
   ```bash
   python -m spacy download de_core_news_md
   ```

2. **Playwright Browser** (optional für JavaScript-Rendering):
   ```bash
   playwright install chromium
   ```

3. **Geo-Visualisierung** benötigt KEINE zusätzlichen Dependencies (nutzt vorhandenes Plotly)

---

## ✅ Verfication

Nach Installation prüfen:

```bash
# Core Features
python -c "import streamlit; print('✅ Streamlit OK')"
python -c "import plotly; print('✅ Plotly OK')"
python -c "import spacy; print('✅ spaCy OK')"

# OCR (optional)
python -c "import PIL; print('✅ Pillow OK')" 2>/dev/null || echo "❌ OCR nicht installiert"

# ML (optional)
python -c "import sentence_transformers; print('✅ Transformers OK')" 2>/dev/null || echo "❌ ML nicht installiert"

# DB (optional)
python -c "import psycopg2; print('✅ PostgreSQL OK')" 2>/dev/null || echo "❌ DB nicht installiert"
```

---

**Viel Erfolg! 🚀**
