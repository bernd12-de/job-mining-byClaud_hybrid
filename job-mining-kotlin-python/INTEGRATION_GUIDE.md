# 🔄 INTEGRATION GUIDE - PostgreSQL + Python + Kotlin

**Vollständige Hybrid-Integration für echte Daten**

---

## 📋 Inhaltsverzeichnis

1. [Setup PostgreSQL](#1-setup-postgresql)
2. [Python Backend starten](#2-python-backend-starten)
3. [Daten senden (Python)](#3-daten-senden-python)
4. [Daten senden (Kotlin)](#4-daten-senden-kotlin)
5. [Dashboard testen](#5-dashboard-testen)
6. [Production Deployment](#6-production-deployment)

---

## 1️⃣ Setup PostgreSQL

### A) Lokal mit Docker

```bash
# PostgreSQL Container starten
docker run --name jobmining-postgres \
  -e POSTGRES_DB=jobmining \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:15

# Warten bis DB ready
sleep 5

# Schema laden
docker exec -i jobmining-postgres psql -U postgres -d jobmining < database/schema.sql
```

### B) Lokale Installation

```bash
# PostgreSQL installieren (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# PostgreSQL starten
sudo systemctl start postgresql

# Datenbank erstellen
sudo -u postgres psql
CREATE DATABASE jobmining;
\q

# Schema laden
psql -U postgres -d jobmining -f database/schema.sql
```

### C) Environment Variables setzen

```bash
# .env Datei erstellen (python-backend/.env)
cat > python-backend/.env <<EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=jobmining
DB_USER=postgres
DB_PASSWORD=postgres
DB_MIN_CONN=2
DB_MAX_CONN=10
EOF
```

### Verification

```bash
# Verbindung testen
psql -U postgres -h localhost -d jobmining -c "SELECT 'Connected!' as status;"

# Tabellen prüfen
psql -U postgres -h localhost -d jobmining -c "\dt"

# Sample-Daten prüfen
psql -U postgres -h localhost -d jobmining -c "SELECT COUNT(*) FROM jobs;"
```

---

## 2️⃣ Python Backend starten

### A) Dependencies installieren

```bash
cd python-backend

# Virtual Environment (falls nicht vorhanden)
python3 -m venv venv
source venv/bin/activate

# PostgreSQL Dependencies
pip install psycopg2-binary  # oder psycopg2 (benötigt libpq-dev)

# Bestehende Dependencies
pip install -r requirements.txt
```

### B) Backend starten

```bash
# Mit DB-Integration
python api_with_db.py

# Output:
# 🚀 Starting FastAPI with PostgreSQL...
# ✅ DB Pool initialized: localhost:5432/jobmining
# ✅ Database initialized
# INFO:     Uvicorn running on http://0.0.0.0:5000
```

### C) API testen

```bash
# Root endpoint
curl http://localhost:5000/

# Stats (prüft DB-Connection)
curl http://localhost:5000/api/stats

# Geo-Heatmap (mit echten Daten aus DB)
curl "http://localhost:5000/api/dashboard/geo-heatmap?year=2025&role=Software%20Developer"
```

---

## 3️⃣ Daten senden (Python)

### A) Externes Python-Programm

```bash
# Zum Beispiel-Ordner wechseln
cd examples

# Sender ausführen
python external_python_sender.py

# Output:
# ============================================================
# External Python Job Data Sender
# ============================================================
#
# 1️⃣ Generating sample jobs...
# 2️⃣ Sending jobs to API...
# ✅ Successfully sent 20 jobs
```

### B) Eigenes Programm erstellen

```python
import requests
from datetime import datetime

# Job-Daten vorbereiten
jobs = [
    {
        "title": "Senior Python Developer",
        "role": "Software Developer",
        "city": "Berlin",
        "country": "DE",
        "latitude": 52.52,
        "longitude": 13.40,
        "posted_at": "2025-12-27T10:00:00",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "source": "my_scraper"
    }
]

# An API senden
response = requests.post(
    "http://localhost:5000/api/data/ingest",
    json=jobs
)

print(response.json())
# {'status': 'success', 'count': 1, 'message': 'Successfully ingested 1 jobs'}
```

### C) CSV-Import

```python
from examples.external_python_sender import JobDataSender

sender = JobDataSender()

# CSV importieren
jobs = sender.import_from_csv("your_jobs.csv")

# An API senden
result = sender.send_jobs(jobs)
print(f"Imported {result['count']} jobs")
```

**CSV Format:**
```csv
title,role,city,country,latitude,longitude,posted_at,skills
"Software Developer (m/w/d)",Software Developer,Berlin,DE,52.52,13.40,2025-12-27T10:00:00,"Python,Docker,Git"
```

---

## 4️⃣ Daten senden (Kotlin)

### A) Kotlin Client nutzen

```kotlin
// Im Kotlin-Projekt
import com.jobmining.client.PythonApiClient

fun main() {
    val client = PythonApiClient()

    // 1. API-Status prüfen
    if (!client.isApiAvailable()) {
        println("Python API ist nicht erreichbar!")
        return
    }

    // 2. Sample-Jobs generieren
    val jobs = client.generateSampleJobs(count = 10)

    // 3. An Python API senden
    val response = client.sendJobs(jobs)
    println("✅ ${response.message}")
}
```

### B) Als Spring Boot Service

```kotlin
// In deinem Spring Boot Service
@Service
class JobImportService(
    private val pythonApiClient: PythonApiClient
) {

    fun importJobsFromDatabase() {
        // 1. Jobs aus eigener DB laden
        val jobs = jobRepository.findAll()

        // 2. In Python-Format konvertieren
        val pythonJobs = jobs.map { job ->
            PythonApiClient.JobInputDto(
                title = job.title,
                role = job.role,
                city = job.location.city,
                latitude = job.location.lat,
                longitude = job.location.lon,
                postedAt = job.postedAt.toString(),
                skills = job.skills.map { it.name },
                source = "kotlin_spring_boot"
            )
        }

        // 3. An Python API senden
        val result = pythonApiClient.sendJobs(pythonJobs)
        logger.info("✅ Sent ${result.count} jobs to Python API")
    }
}
```

### C) Standalone Kotlin-Programm ausführen

```bash
# Kotlin-Programm kompilieren und ausführen
cd kotlin-backend/src/main/kotlin/com/jobmining/client

# Mit kotlinc (wenn installiert)
kotlinc PythonApiClient.kt -include-runtime -d PythonApiClient.jar
java -jar PythonApiClient.jar

# Oder mit Gradle
cd kotlin-backend
./gradlew run
```

---

## 5️⃣ Dashboard testen

### A) Browser öffnen

```bash
# Dashboard mit Karte
open http://localhost:5000/dashboard/map

# Oder
firefox http://localhost:5000/dashboard/map
```

### B) Filter testen

1. **Jahr-Filter:**
   - Wähle verschiedene Jahre (2020-2025)
   - Beobachte wie sich Job-Zahlen ändern

2. **Berufs-Filter:**
   - Wähle "Software Developer"
   - Sehe Top-10 Kompetenzen (Python, Java, Docker, etc.)
   - Wechsle zu "Data Scientist"
   - Sehe neue Kompetenzen (Machine Learning, TensorFlow, etc.)

3. **X-Marker:**
   - Mehr Jobs → Mehr X-Symbole (✖✖✖✖)
   - Weniger Jobs → Weniger X-Symbole (✖✖)

### C) API-Calls manuell

```bash
# Alle Jobs für 2025
curl "http://localhost:5000/api/dashboard/geo-heatmap?year=2025"

# Software Developer Jobs in 2024
curl "http://localhost:5000/api/dashboard/geo-heatmap?year=2024&role=Software%20Developer"

# Data Scientist Jobs (alle Jahre)
curl "http://localhost:5000/api/dashboard/geo-heatmap?role=Data%20Scientist"

# Statistiken
curl http://localhost:5000/api/stats
```

---

## 6️⃣ Production Deployment

### A) Docker Compose (Empfohlen)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: jobmining
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

  python-backend:
    build: ./python-backend
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: jobmining
      DB_USER: ${DB_USER:-postgres}
      DB_PASSWORD: ${DB_PASSWORD:-postgres}
    ports:
      - "5000:5000"
    depends_on:
      - postgres
    restart: unless-stopped

  kotlin-backend:
    build: ./kotlin-backend
    environment:
      PYTHON_API_URL: http://python-backend:5000
    ports:
      - "8080:8080"
    depends_on:
      - python-backend
    restart: unless-stopped

volumes:
  postgres_data:
```

**Starten:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### B) Kubernetes (Advanced)

```yaml
# k8s/postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: jobmining
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
```

**Deploy:**
```bash
kubectl apply -f k8s/
```

### C) Cloud-Managed DB (AWS RDS, Google Cloud SQL)

```bash
# Environment Variables setzen
export DB_HOST=jobmining.abc123.eu-central-1.rds.amazonaws.com
export DB_PORT=5432
export DB_NAME=jobmining
export DB_USER=admin
export DB_PASSWORD=secure_password

# Python Backend starten
cd python-backend
python api_with_db.py
```

---

## 🔧 Troubleshooting

### Problem: "Connection refused" (PostgreSQL)

```bash
# Prüfe ob PostgreSQL läuft
sudo systemctl status postgresql

# Prüfe Port
netstat -an | grep 5432

# Prüfe Docker Container
docker ps | grep postgres
docker logs jobmining-postgres
```

### Problem: "psycopg2 not found"

```bash
# Linux: Installiere libpq-dev
sudo apt install libpq-dev python3-dev

# Installiere psycopg2
pip install psycopg2-binary
```

### Problem: "Database does not exist"

```bash
# Datenbank erstellen
docker exec -it jobmining-postgres psql -U postgres -c "CREATE DATABASE jobmining;"

# Schema laden
docker exec -i jobmining-postgres psql -U postgres -d jobmining < database/schema.sql
```

### Problem: "No data in dashboard"

```bash
# 1. Prüfe ob Sample-Daten vorhanden
psql -U postgres -h localhost -d jobmining -c "SELECT COUNT(*) FROM jobs;"

# 2. Sende Test-Daten
cd examples
python external_python_sender.py

# 3. Prüfe API
curl "http://localhost:5000/api/dashboard/geo-heatmap?year=2025"
```

---

## 📊 Datenfluss-Übersicht

```
┌─────────────────┐
│  Python Sender  │────┐
└─────────────────┘    │
                       │
┌─────────────────┐    │    ┌──────────────────┐    ┌────────────────┐
│  Kotlin Client  │────┼───→│  FastAPI Backend │───→│  PostgreSQL DB │
└─────────────────┘    │    │  (api_with_db.py)│    │  (jobmining)   │
                       │    └──────────────────┘    └────────────────┘
┌─────────────────┐    │              ↓
│  CSV Import     │────┘              ↓
└─────────────────┘         ┌──────────────────┐
                            │  Dashboard Map   │
                            │  (Leaflet.js)    │
                            └──────────────────┘
```

---

## ✅ Checkliste für Production

- [ ] PostgreSQL mit Backup konfiguriert
- [ ] Environment Variables in `.env` (nicht in Git!)
- [ ] DB Connection Pool konfiguriert (min: 2, max: 10)
- [ ] SSL/TLS für DB-Verbindung aktiviert
- [ ] API mit Gunicorn (nicht Uvicorn direkt)
- [ ] Nginx Reverse Proxy konfiguriert
- [ ] Logging konfiguriert (Logstash, CloudWatch, etc.)
- [ ] Monitoring (Prometheus, Grafana)
- [ ] Rate Limiting aktiviert
- [ ] CORS richtig konfiguriert

---

## 📚 Weiterführende Docs

- [START_GUIDE.md](START_GUIDE.md) - Deployment-Szenarien
- [database/schema.sql](database/schema.sql) - DB-Schema
- [api_with_db.py](python-backend/api_with_db.py) - API-Implementierung
- [PythonApiClient.kt](kotlin-backend/src/main/kotlin/com/jobmining/client/PythonApiClient.kt) - Kotlin Client

---

**Version:** 1.0
**Letztes Update:** 2025-12-27
**Autor:** Claude Code Integration
