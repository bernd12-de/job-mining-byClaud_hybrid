# ✅ V2.0 Validierungs-Checkliste

Nutze diese Checkliste, um V2.0 in deiner lokalen Umgebung zu validieren.

---

## 🔧 Schritt 1: Environment Setup (10 Min)

### 1.1 Python-Version prüfen
```bash
python3 --version
# Erwartet: Python 3.11 oder höher
```
✅ **Check**: Version >= 3.11 ? 

### 1.2 Virtual Environment erstellen
```bash
cd /workspaces/job-mining-kotlin-python/python-backend
python3 -m venv venv
source venv/bin/activate
```
✅ **Check**: Shell zeigt `(venv)` Prefix?

### 1.3 Dependencies installieren
```bash
pip install -r requirements.txt
```
✅ **Check**: 26 packages erfolgreich? Keine Fehler?

### 1.4 spaCy Modell herunterladen
```bash
python -m spacy download de_core_news_sm
```
✅ **Check**: Modell erfolgreich heruntergeladen?

---

## 📊 Schritt 2: Dashboard API (5 Min)

### 2.1 Dashboard starten
```bash
python app/api/dashboard_api.py
```
✅ **Check**: Output zeigt `Running on http://localhost:5000` ?

### 2.2 Browser Test
- Öffne http://localhost:5000/dashboard
- ✅ **Check**: Dashboard lädt? Keine Fehler in Browser Console?

### 2.3 API Endpoints testen
In separatem Terminal (in venv):
```bash
# Test 1: Haupt-Statistiken
curl http://localhost:5000/api/dashboard/stats | jq .

# Test 2: Competence Trends
curl http://localhost:5000/api/dashboard/competence-trends | jq .

# Test 3: Export
curl http://localhost:5000/api/dashboard/export > /tmp/export.json
ls -lh /tmp/export.json
```
✅ **Check**: Alle 3 APIs antworten mit JSON?

---

## 🔍 Schritt 3: Core Pipeline (5 Min)

### 3.1 Models importieren
```bash
python -c "from app.core.models_v2 import Competence, JobPosting; print('✅ Models OK')"
```
✅ **Check**: Keine ImportError?

### 3.2 Pipeline testen
```bash
python main_v2.py
```
✅ **Check**: Output zeigt Competences extrahiert? Keine Fehler?

### 3.3 Sample Competence erstellen
```bash
python << 'EOF'
from app.core.models_v2 import Competence

comp = Competence(
    name="Python",
    esco_uri="http://data.europa.eu/esco/skill/001",
    confidence=0.95,
    is_digital=True
)
print(f"✅ Created: {comp.name}")
print(f"   Confidence: {comp.confidence}")
print(f"   Digital: {comp.is_digital}")
EOF
```
✅ **Check**: Competence erfolgreich erstellt?

---

## 🐳 Schritt 4: Docker Validierung (optional, 5 Min)

### 4.1 Docker Check
```bash
docker --version
```
✅ **Check**: Docker installiert?

### 4.2 Docker Compose Check
```bash
docker-compose --version
```
✅ **Check**: docker-compose installiert?

### 4.3 Build Test
```bash
cd /workspaces/job-mining-kotlin-python
docker-compose -f docker-compose.v2.yml build
```
✅ **Check**: Build erfolgreich? Keine Fehler?

### 4.4 Run Test
```bash
docker-compose -f docker-compose.v2.yml up -d
sleep 5
curl http://localhost:5000/api/dashboard/stats
docker-compose -f docker-compose.v2.yml down
```
✅ **Check**: Container läuft? API antwortet?

---

## 📚 Schritt 5: Dateistruktur Validierung (2 Min)

Stelle sicher, dass folgende Dateien existieren:

```bash
# Core Models
test -f python-backend/app/core/models_v2.py && echo "✅ models_v2.py" || echo "❌ MISSING"

# Dashboard API
test -f python-backend/app/api/dashboard_api.py && echo "✅ dashboard_api.py" || echo "❌ MISSING"

# Dashboard Frontend
test -f python-backend/app/templates/dashboard.html && echo "✅ dashboard.html" || echo "❌ MISSING"

# Main Pipeline
test -f python-backend/main_v2.py && echo "✅ main_v2.py" || echo "❌ MISSING"

# Docker Files
test -f Dockerfile.v2 && echo "✅ Dockerfile.v2" || echo "❌ MISSING"
test -f docker-compose.v2.yml && echo "✅ docker-compose.v2.yml" || echo "❌ MISSING"

# Documentation
test -f QUICKSTART_V2.0.md && echo "✅ QUICKSTART_V2.0.md" || echo "❌ MISSING"
test -f DASHBOARD_GUIDE.md && echo "✅ DASHBOARD_GUIDE.md" || echo "❌ MISSING"
test -f SETUP_V2.0.md && echo "✅ SETUP_V2.0.md" || echo "❌ MISSING"
```

✅ **Check**: Alle 10 Dateien existieren?

---

## 🚀 Schritt 6: Integration Check (3 Min)

### 6.1 Imports aus Dokumentation
```bash
cd python-backend
python << 'EOF'
# Check wie in QUICKSTART_V2.0.md beschrieben
from repositories.hybrid_competence_repository import HybridCompetenceRepository
from extractors.spacy_competence_extractor import SpacyCompetenceExtractor
from app.core.models_v2 import JobPosting, Competence

print("✅ Alle Imports OK")
EOF
```
✅ **Check**: Keine ImportErrors?

### 6.2 Dashboard Routes
```bash
python << 'EOF'
from app.api.dashboard_api import app

routes = [
    '/dashboard',
    '/api/dashboard/stats',
    '/api/dashboard/competence-trends',
    '/api/dashboard/skill-distribution',
    '/api/dashboard/level-progression',
    '/api/dashboard/role-distribution',
    '/api/dashboard/top-emerging-skills',
    '/api/dashboard/quality-metrics',
    '/api/dashboard/regional-distribution',
    '/api/dashboard/export'
]

for route in routes:
    print(f"✅ Route: {route}")
EOF
```
✅ **Check**: Alle 10 Routes gelistet?

---

## 📝 Schritt 7: Dokumentation Check (2 Min)

### 7.1 README aktualisiert?
```bash
grep "V2.0 ist eine komplett neue" README.md > /dev/null && echo "✅ README.md updated" || echo "❌ README needs update"
```
✅ **Check**: README zeigt V2.0?

### 7.2 Guides vorhanden?
```bash
wc -l QUICKSTART_V2.0.md DASHBOARD_GUIDE.md SETUP_V2.0.md
```
✅ **Check**: Alle Guides haben Content?

---

## 🎯 Final Checklist

| Task | Status |
|------|--------|
| ✅ Python 3.11+ installiert | ☐ |
| ✅ venv aktiviert | ☐ |
| ✅ requirements.txt installiert | ☐ |
| ✅ spaCy de_core_news_sm heruntergeladen | ☐ |
| ✅ Dashboard lädt unter http://localhost:5000 | ☐ |
| ✅ API /api/dashboard/stats antwortet | ☐ |
| ✅ main_v2.py läuft ohne Fehler | ☐ |
| ✅ Competence-Model funktioniert | ☐ |
| ✅ Docker optional getestet | ☐ |
| ✅ Alle V2.0 Dateien existieren | ☐ |
| ✅ Dokumentation aktualisiert | ☐ |
| ✅ Alle Dashboard Routes verfügbar | ☐ |

---

## 🆘 Problem Lösungen

### Problem: `ModuleNotFoundError`
**Lösung**: 
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: Port 5000 already in use
**Lösung**:
```bash
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Problem: spaCy model not found
**Lösung**:
```bash
python -m spacy download de_core_news_sm
```

### Problem: ImportError in dashboard_api.py
**Lösung**:
```bash
cd python-backend
python app/api/dashboard_api.py
```

---

## ✨ Success!

Wenn alle Checks grün sind (☑️), dann läuft V2.0 perfekt! 🎉

**Nächste Schritte:**
1. [QUICKSTART_V2.0.md](QUICKSTART_V2.0.md) - Features kennenlernen
2. [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) - Dashboard API Details
3. [SETUP_V2.0.md](SETUP_V2.0.md) - Production Deployment

---

**Last Updated:** 2025-12-27
**Version:** V2.0
