# Dashboard — Run‑Anleitung & Beschreibung

Dieses Dokument beschreibt, wie Sie das minimal implementierte Dashboard (Streamlit) und die zugehörigen Export‑Endpunkte betreiben und testen.

## Lokaler Betrieb (Entwicklung)
1. In das Python Backend wechseln:

   cd python-backend

2. Virtuelle Umgebung erstellen / aktivieren (Python 3.11 empfohlen):

   python3 -m venv .venv
   source .venv/bin/activate

3. Abhängigkeiten installieren:

   pip install -r requirements.txt

4. Streamlit starten (entwicklerfreundlich):

   streamlit run dashboard_app.py

   Das Dashboard ist erreichbar unter: http://localhost:8501

5. Alternativ: nur API starten (FastAPI):

   uvicorn main:app --reload --port 8000

   API-Dokumentation: http://localhost:8000/docs

## Docker / Docker Compose (empfohlen für Integration)

Der `docker-compose.yml` enthält jetzt einen `streamlit` Service.

Starten Sie die komplette Umgebung (DB, Kotlin, Python, Streamlit):

   docker compose up -d jobmining-db python-backend streamlit

Anschließend:
- FastAPI: http://localhost:8000/docs
- Streamlit Dashboard: http://localhost:8501

## Wichtige Endpunkte
- GET /reports/dashboard-metrics
  - Liefert: total_jobs, total_skills, top_skills (Liste), domain_mix, time_series
  - Beispiel: curl "http://localhost:8000/reports/dashboard-metrics"

- GET /reports/export.csv
  - Download: CSV mit einer Zeile pro Job
  - Beispiel: curl -O "http://localhost:8000/reports/export.csv"

- GET /reports/export.pdf
  - Download: Einfacher PDF‑Report (Prototyp)
  - Beispiel: curl -O "http://localhost:8000/reports/export.pdf"

## Hinweise & Empfehlungen
- Der Streamlit‑Prototyp ist bewusst minimal: für Produktion sollten Authentifizierung, Caching und Hintergrundjobs (z.B. Periodische Updates) ergänzt werden.
- Die Datenquelle sind die batch-Resultate unter `python-backend/data/exports/batch_results` (wird vom Batch-Prozess erzeugt).
- Für umfangreichere Reports und Grafiken kann der PDF‑Generator (ReportLab) erweitert werden.

## Troubleshooting
- Keine Daten im Dashboard?
  - Prüfen Sie, ob `python-backend/data/exports/batch_results/summary.json` existiert und `processed > 0`.
  - Wenn nicht, starten Sie die Batch-Analyse (`POST /batch-process`) oder legen Sie Beispiel‑JSONs in den Ordner.

- Portkonflikte:
  - Streamlit: standardmäßig 8501
  - FastAPI: standardmäßig 8000


---
