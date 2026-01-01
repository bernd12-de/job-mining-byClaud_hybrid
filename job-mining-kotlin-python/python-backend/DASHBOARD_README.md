# 📊 Multi-Page Dashboard - Benutzerhandbuch

## 🎯 Übersicht

Das neue **Multi-Page Dashboard** ist eine vollständig überarbeitete Benutzeroberfläche mit:

- ✅ **6 Seiten**: Home, Trends, Rollen, ESCO Landkarte, Discovery, Jobs
- ✅ **ESCO Integration**: 15.719 Skills vollständig integriert
- ✅ **7-Ebenen-Modell**: Visualisierung aller 5 Ebenen
- ✅ **Discovery Learning**: Neue Skills Management
- ✅ **Rollenanalyse**: 30+ Rollen mit Evolution
- ✅ **Charts & Visualisierungen**: 10+ interaktive Dashboards

---

## 📁 Struktur

```
python-backend/
├── Home.py                          # 🏠 Hauptseite (Overview)
├── pages/                           # 📂 Unterseiten
│   ├── 1_📈_Trends.py               # Skills-Zeitreihe, Emerging Skills
│   ├── 2_👤_Rollen.py               # Rollenanalyse, Network Graph
│   ├── 3_🗺️_ESCO_Landkarte.py      # 7-Ebenen-Modell
│   ├── 4_🔍_Discovery.py            # Neue Skills Management
│   └── 5_💼_Jobs.py                 # Jobs-Übersicht
├── dashboard_app.py                 # ⚠️ Altes Dashboard (deprecated)
└── tests/
    └── test_new_dashboard.py        # 🧪 Test Suite
```

---

## 🚀 Schnellstart

### 1. Services starten

**Terminal 1: Python Backend**
```bash
cd python-backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2: Kotlin Backend**
```bash
cd kotlin-api
./gradlew bootRun
```

**Terminal 3: Streamlit Dashboard**
```bash
cd python-backend
streamlit run Home.py --server.port 8501
```

### 2. Dashboard öffnen

```
http://localhost:8501
```

---

## 📊 Seiten-Übersicht

### 🏠 Home (Overview)

**Features:**
- Service-Status (Python, Kotlin, DB, Streamlit)
- Stats-Karten (Jobs, Skills, Neue Skills, Cluster)
- Quick Links (API Docs, Health Check)
- Navigation zu allen Unterseiten

**URL:** `http://localhost:8501`

---

### 📈 Trends

**Features:**
- **Skills & Tools Zeitreihe**: Multi-Line Chart (2020-2025)
- **Emerging Skills**: Top 10 mit Wachstum %
- **Rollen im Wandel**: Evolution-Tabelle

**Datenquellen:**
- ESCO Skills (Kotlin API)
- Discovery Candidates (Python API)
- Jobs (Kotlin API)

---

### 👤 Rollen

**Features:**
- **Rollenanalyse**: 3-Phasen-Evolution (Traditionell → Neu → Technisch)
- **Timeline-Visualisierung**: 2012 → 2024
- **Network Graph**: Verwandte Rollen (Berührungspunkte)
- **Top Skills pro Rolle**

**Verfügbare Rollen:**
- Data Scientist
- Fullstack Developer
- DevOps Engineer
- 27+ weitere Rollen

---

### 🗺️ ESCO Landkarte

**Features:**
- **7-Ebenen-Verteilung**: Sunburst + Bar Chart
- **Level-Details**: Academia → Discovery
- **Skill-Explorer**: 15.719 ESCO Skills durchsuchbar
- **Top Skills aus Jobs**

**7-Ebenen-Modell:**
1. **Level 5 (Academia)**: 46 Skills aus Modulhandbüchern
2. **Level 4 (Fachbuch)**: 60 Skills aus Fachliteratur
3. **Level 3 (Digital)**: 3.500 Digital-Skills (auto-erkannt)
4. **Level 2 (ESCO)**: 15.171 Standard-Skills
5. **Level 1 (Discovery)**: 80 neu entdeckte Skills

---

### 🔍 Discovery

**Features:**
- **Discovery Candidates**: Neue Skills, Rollen, Industrien
- **Approve/Ignore System**: Admin-Validierung
- **Auto-Promotion**: 5× → L2, 10× → L3
- **Statistik**: Level-Verteilung, Type-Verteilung

**Workflow:**
1. System findet unbekannten Skill
2. Erstellt Candidate (Level 1)
3. Bei Wiederholung: Auto-Promotion
4. Admin validiert → Höheres Level

---

### 💼 Jobs

**Features:**
- **Jobs-Übersicht**: Paginierte Tabelle
- **Job-Details**: Skills, Unternehmen, Ort
- **Export**: CSV-Download
- **Pagination**: 10/20/50/100 pro Seite

---

## 🧪 Tests

### Manuelle Tests

**1. Navigation testen**
```bash
cd python-backend
ls -lh Home.py pages/*.py
```

**Erwartung:** Alle 6 Dateien existieren

**2. Syntax-Check**
```bash
python3 -m py_compile Home.py pages/*.py
```

**Erwartung:** Keine Fehler

**3. API-Endpunkte testen**
```bash
# Python Backend
curl http://localhost:8000/health

# Kotlin Backend
curl http://localhost:8080/actuator/health

# ESCO Skills
curl http://localhost:8080/api/v1/rules/esco-full | head -100

# Discovery Candidates
curl http://localhost:8000/discovery/candidates
```

**4. Dashboard starten**
```bash
streamlit run Home.py
```

**Erwartung:** Dashboard lädt ohne Fehler

---

### Pytest Tests (Optional)

```bash
pip install pytest requests pandas
python3 -m pytest tests/test_new_dashboard.py -v
```

**Tests:**
- ✅ API Endpunkte (/health, /discovery)
- ✅ ESCO-Daten laden (15.719 Skills)
- ✅ DB-Verbindung & Queries
- ✅ Navigation (Dateien existieren)
- ✅ Stats-Karten (Daten abrufbar)
- ✅ Charts (Daten-Generierung)

---

## 🐛 Troubleshooting

### Problem: "Connection refused" bei API-Aufrufen

**Lösung:**
1. Prüfe ob Backend-Services laufen:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8080/actuator/health
   ```

2. Starte Services neu (siehe "Schnellstart")

---

### Problem: "ESCO-Daten nicht geladen"

**Lösung:**
1. Prüfe Kotlin Backend:
   ```bash
   curl http://localhost:8080/api/v1/rules/esco-full | jq length
   ```

2. Erwartung: `15719` (oder ähnlich)

---

### Problem: "Discovery Candidates leer"

**Lösung:**
1. Analysiere erste Stellenanzeige:
   ```bash
   curl -X POST http://localhost:8000/analyse/file \
     -F "file=@test-data/test-stellenanzeige.txt"
   ```

2. Prüfe Candidates:
   ```bash
   curl http://localhost:8000/discovery/candidates
   ```

---

## 📚 Dokumentation

**Weitere Guides:**
- `STATUS_REPORT.md` - Vollständiger System-Status
- `ESCO_7_EBENEN_STATUS.md` - 7-Ebenen-Modell Details
- `UI_DASHBOARD_STATUS.md` - Dashboard Features
- `TESTING.md` - Test-Suite (46 Tests)

---

## 🎯 Features-Übersicht

| Feature | Status | Seite |
|---------|--------|-------|
| Service-Status | ✅ | Home |
| Stats-Karten | ✅ | Home |
| Skills-Zeitreihe | ✅ | Trends |
| Emerging Skills | ✅ | Trends |
| Rollenanalyse | ✅ | Rollen |
| Network Graph | ✅ | Rollen |
| 7-Ebenen-Verteilung | ✅ | ESCO Landkarte |
| Skill-Explorer | ✅ | ESCO Landkarte |
| Discovery Management | ✅ | Discovery |
| Jobs-Übersicht | ✅ | Jobs |
| Export CSV | ✅ | Jobs |

---

## 🔧 Technische Details

**Frontend:**
- Streamlit 1.x
- Plotly Express & Graph Objects
- Pandas
- NetworkX (für Graphs)

**Backend:**
- FastAPI (Python)
- Spring Boot (Kotlin)
- PostgreSQL

**APIs:**
- Python: `http://localhost:8000`
- Kotlin: `http://localhost:8080`

---

## 📊 Performance

- **Home.py**: 9.2 KB
- **Trends**: 12 KB
- **Rollen**: 14 KB
- **ESCO Landkarte**: 12 KB
- **Discovery**: 5.1 KB
- **Jobs**: 3.1 KB

**Gesamt**: ~55 KB Code für 6 Seiten

---

## ✅ Checkliste: Dashboard-Start

- [ ] Python Backend läuft (`curl http://localhost:8000/health`)
- [ ] Kotlin Backend läuft (`curl http://localhost:8080/actuator/health`)
- [ ] ESCO-Daten geladen (15.719 Skills)
- [ ] Dashboard gestartet (`streamlit run Home.py`)
- [ ] Browser öffnet `http://localhost:8501`
- [ ] Home-Seite zeigt Service-Status
- [ ] Navigation zu allen Unterseiten funktioniert
- [ ] Charts rendern korrekt

---

**Erstellt:** 2025-12-30
**Version:** 1.0.0
**Status:** ✅ Produktiv einsetzbar
