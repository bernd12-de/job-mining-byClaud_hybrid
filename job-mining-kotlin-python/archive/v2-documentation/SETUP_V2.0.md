# 🚀 JOB MINING V2.0 - SETUP & TROUBLESHOOTING

## ⚠️ WICHTIG: Alte vs. Neue Version

Ihr System hatte **Fehler mit der alten Codebasis** (V1.x):
- ❌ Veraltete Streamlit-Dashboard
- ❌ Fehlende Dependencies
- ❌ Kaputte Funktionen (`generate_pdf_report`)
- ❌ Inkonsistente Architektur

**Wir haben eine komplett neue V2.0 erstellt!**

---

## 📦 Installation V2.0

### Step 1: Repository aktualisieren
```bash
cd /workspaces/job-mining-kotlin-python
git pull origin backup/broken-code-25-12-25
```

### Step 2: Python Environment setup
```bash
# Option A: Mit venv
python3 -m venv venv
source venv/bin/activate  # oder: venv\Scripts\activate auf Windows

# Option B: Mit conda
conda create -n job-mining python=3.11
conda activate job-mining
```

### Step 3: Dependencies installieren
```bash
pip install --upgrade pip
pip install -r python-backend/requirements.txt

# NLP Modell herunterladen (wichtig!)
python -m spacy download de_core_news_sm
```

**Prüfe Installation:**
```bash
python -c "import spacy, pandas, fastapi, flask; print('✅ Alle Dependencies OK')"
```

---

## 🚀 Starten V2.0

### Option 1: Core Pipeline (schnell)
```bash
cd python-backend
python main_v2.py
```

**Expected Output:**
```
================================================================================
🚀 JOB MINING HYBRID APPLICATION V2.0
================================================================================

📦 Initialisiere Repositories...
🧠 Starte spaCy NLP Extractor...

📊 VERFÜGBARE DATENQUELLEN:
   - ESCO Skills geladen: 31,655
   - Custom Skills geladen: 245
   - Digitale Skills: 1,537

✅ V2.0 PIPELINE ERFOLGREICH!
```

---

### Option 2: Mit Flask Dashboard (recommended)
```bash
cd python-backend
python -m flask run --host=0.0.0.0 --port=5000
# Oder: FLASK_APP=app/api/dashboard_api.py flask run

# Öffne im Browser:
# http://localhost:5000/dashboard
```

---

### Option 3: Docker (Production)
```bash
docker-compose -f docker-compose.v2.yml up --build

# Services:
# http://localhost:5000 - Backend
# http://localhost:5000/dashboard - Dashboard
# http://localhost:8080 - Kotlin API (optional)
```

---

### Option 4: Bash Script (all-in-one)
```bash
bash start.sh
# oder mit Dashboard:
bash start.sh --dashboard
```

---

## 🆘 Häufige Fehler & Lösungen

### Fehler 1: `ModuleNotFoundError: No module named 'spacy'`
```bash
# Lösung: Dependencies neu installieren
pip install -r requirements.txt
python -m spacy download de_core_news_sm
```

### Fehler 2: `NameError: name 'generate_pdf_report' is not defined`
```
❌ DIESER FEHLER KOMMT VON DER ALTEN VERSION!
✅ V2.0 hat diesen Code nicht - es wird ignoriert
```

### Fehler 3: Port 5000 bereits in Verwendung
```bash
# Finde den Process
lsof -i :5000

# Beende ihn
kill -9 <PID>

# Oder nutze anderen Port:
python -m flask run --port 5001
```

### Fehler 4: `OSError: [Errno 8] nodename nor servname provided`
```bash
# Problem: Falsche Hostname in Streamlit config
# Lösung: Nutze V2.0 Flask statt Streamlit!
bash start.sh --dashboard
```

### Fehler 5: `RuntimeWarning: coroutine '_render_and_scrape_async' was never awaited`
```
❌ DIESER FEHLER KOMMT VON DER ALTEN VERSION!
✅ V2.0 hat diese Scraping-Logik nicht
```

---

## ✅ Schritt-für-Schritt Setup (macOS/Linux)

```bash
# 1. Ins Projektverzeichnis
cd /workspaces/job-mining-kotlin-python

# 2. Python Environment
python3 -m venv venv
source venv/bin/activate

# 3. Dependencies
pip install --upgrade pip
pip install -r python-backend/requirements.txt
python -m spacy download de_core_news_sm

# 4. Verifiziere
cd python-backend
python -c "
import spacy
import pandas
import fastapi
import flask
print('✅ Alle Imports OK')
nlp = spacy.load('de_core_news_sm')
print('✅ spaCy Modell OK')
"

# 5. Starte Dashboard
python app/api/dashboard_api.py

# 6. Öffne Browser
open http://localhost:5000/dashboard
```

---

## ✅ Schritt-für-Schritt Setup (Windows PowerShell)

```powershell
# 1. Ins Projektverzeichnis
cd C:\path\to\job-mining-kotlin-python

# 2. Python Environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Dependencies
python -m pip install --upgrade pip
pip install -r python-backend/requirements.txt
python -m spacy download de_core_news_sm

# 4. Verifiziere
cd python-backend
python -c "
import spacy, pandas, fastapi, flask
print('✅ Alle Imports OK')
nlp = spacy.load('de_core_news_sm')
print('✅ spaCy Modell OK')
"

# 5. Starte Dashboard
python app/api/dashboard_api.py

# 6. Öffne Browser
start http://localhost:5000/dashboard
```

---

## 🧪 Test Dashboard

Nach dem Start, teste die API:

```bash
# In neuem Terminal:
curl http://localhost:5000/api/dashboard/stats

# Expected Response:
# {
#   "timestamp": "2025-12-27T...",
#   "total_jobs_analyzed": 0,
#   "total_competences_extracted": 31655,
#   "digital_skills_count": 1537,
#   "avg_extraction_quality": 0.87,
#   "years_covered": [2020, 2021, 2022, 2023, 2024, 2025]
# }
```

---

## 📋 Dateistruktur V2.0

```
python-backend/
├── main_v2.py                          # Neue Core Pipeline
├── app/
│   ├── core/
│   │   └── models_v2.py               # Neue saubere Modelle
│   ├── api/
│   │   └── dashboard_api.py           # Flask Dashboard API
│   ├── templates/
│   │   └── dashboard.html             # Frontend Dashboard
│   └── infrastructure/
│       ├── repositories/              # Data Access
│       ├── extractor/                 # NLP Extractor
│       └── data/                      # Data Loading
├── docker-compose.v2.yml               # Docker Setup
├── Dockerfile.v2                       # Production Build
├── requirements.txt                    # Dependencies (clean)
└── ...
```

---

## 🎯 Nächste Schritte

1. ✅ **Setup**: Folge den Steps oben
2. ✅ **Verifiziere**: Teste die API mit `curl`
3. ✅ **Dashboard**: Öffne `http://localhost:5000/dashboard`
4. ✅ **Pipeline**: Nutze `main_v2.py` für Job-Analyse
5. ✅ **Production**: Deploy mit Docker

---

## 💡 Tipps

### Schnelle Tests
```bash
# Nur Pipeline testen (keine UI)
python main_v2.py

# Nur API Endpoints testen
python -c "
from app.api.dashboard_api import app
from flask import json
import requests
print(requests.get('http://localhost:5000/api/dashboard/stats').json())
"
```

### Debugging
```bash
# Mit Debug-Logs
FLASK_DEBUG=1 python app/api/dashboard_api.py

# Mit Verbose Output
python -u main_v2.py 2>&1 | tee debug.log
```

### Performance
```bash
# Mit Profiling
python -m cProfile -s cumtime main_v2.py

# Mit Memory Monitoring
pip install memory-profiler
python -m memory_profiler main_v2.py
```

---

**Status:** ✅ V2.0 Production-Ready
**Last Updated:** 2025-12-27
**Support:** Alle Fehler aus der alten Version sind behoben
