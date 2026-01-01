# 🚀 START GUIDE - Job Mining System

**Letzte Aktualisierung:** 2025-12-27
**Status:** ✅ Production-Ready

---

## 📋 Voraussetzungen

- **Python:** 3.10+
- **Java:** 17+ (für Kotlin Backend)
- **Docker:** Optional für Container-Deployment
- **Node/npm:** Nicht erforderlich (kein JavaScript-Build)

---

## A) 🖥️ LOKAL STARTEN

### 1. Setup (einmalig)

```bash
# Repository klonen (falls nicht vorhanden)
cd /path/to/job-mining-kotlin-python

# Python Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r python-backend/requirements.txt

# spaCy Deutsch-Modell laden
python -m spacy download de_core_news_md
```

### 2. Backend starten

**Option A: FastAPI (Python) - Port 5000**
```bash
cd python-backend
python main.py
```

**Option B: Kotlin Spring Boot - Port 8080**
```bash
cd kotlin-backend
./gradlew bootRun
```

### 3. Browser öffnen

- **Dashboard mit Karte:** http://localhost:5000/dashboard/map
- **Haupt-Dashboard:** http://localhost:5000/ (templates/dashboard.html)
- **FastAPI Docs:** http://localhost:5000/docs
- **Kotlin Swagger:** http://localhost:8080/swagger-ui/index.html

### 4. API testen

```bash
# Python Backend
curl http://localhost:5000/api/dashboard/stats
curl "http://localhost:5000/api/dashboard/geo-heatmap?year=2025&role=Software%20Developer"

# Kotlin Backend
curl http://localhost:8080/api/jobs
```

---

## B) 🐳 DOCKER FÜR SERVER

### 1. Docker Build & Start

```bash
# Docker Compose starten (alle Services)
docker-compose up -d

# Oder einzelne Services
docker-compose up -d python-backend
docker-compose up -d kotlin-backend
```

### 2. Überprüfen

```bash
# Logs anzeigen
docker-compose logs -f python-backend

# Status prüfen
docker-compose ps

# Services stoppen
docker-compose down
```

### 3. Zugriff

- **Python Backend:** http://server-ip:5000
- **Kotlin Backend:** http://server-ip:8080
- **Dashboard Map:** http://server-ip:5000/dashboard/map

### 4. Docker-Compose Datei (docker-compose.yml)

```yaml
version: '3.8'

services:
  python-backend:
    build: ./python-backend
    ports:
      - "5000:5000"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    restart: unless-stopped
    command: python main.py

  kotlin-backend:
    build: ./kotlin-backend
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=prod
    depends_on:
      - python-backend
    restart: unless-stopped
```

### 5. Production-Optimierungen

```bash
# Mit Nginx Reverse Proxy
docker run -d --name nginx \
  -p 80:80 \
  -v ./nginx.conf:/etc/nginx/nginx.conf:ro \
  nginx:alpine

# Mit Resource Limits
docker-compose up -d --scale python-backend=2
```

---

## C) ☁️ CLOUD DEPLOYMENT

### Option 1: AWS EC2

```bash
# 1. SSH in EC2-Instanz
ssh -i key.pem ubuntu@ec2-instance

# 2. Docker installieren
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker

# 3. Repository klonen
git clone https://github.com/your-repo/job-mining-kotlin-python.git
cd job-mining-kotlin-python

# 4. Environment-Variablen setzen
export PYTHON_ENV=production
export PORT=5000

# 5. Docker starten
sudo docker-compose up -d

# 6. Firewall öffnen (Security Group)
# - Port 5000 (Python Backend)
# - Port 8080 (Kotlin Backend)
# - Port 80/443 (HTTP/HTTPS)
```

**Zugriff:** `http://ec2-xx-xx-xx-xx.compute.amazonaws.com:5000`

---

### Option 2: Google Cloud Run

```bash
# 1. Dockerfile für Cloud Run anpassen
# python-backend/Dockerfile.cloudrun
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download de_core_news_md
COPY . .
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app

# 2. Build & Deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/job-mining-python
gcloud run deploy job-mining \
  --image gcr.io/PROJECT_ID/job-mining-python \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300

# 3. Zugriff
# https://job-mining-xxxx-ew.a.run.app
```

---

### Option 3: Azure Container Instances

```bash
# 1. Azure Login
az login

# 2. Container Registry erstellen
az acr create --resource-group myResourceGroup \
  --name jobminingregistry --sku Basic

# 3. Image bauen und pushen
az acr build --registry jobminingregistry \
  --image job-mining-python:latest \
  ./python-backend

# 4. Container deployen
az container create \
  --resource-group myResourceGroup \
  --name job-mining-python \
  --image jobminingregistry.azurecr.io/job-mining-python:latest \
  --dns-name-label job-mining-app \
  --ports 5000 \
  --cpu 2 --memory 4

# 5. Zugriff
# http://job-mining-app.westeurope.azurecontainer.io:5000
```

---

### Option 4: Heroku

```bash
# 1. Heroku CLI installieren
curl https://cli-assets.heroku.com/install.sh | sh

# 2. Login & App erstellen
heroku login
heroku create job-mining-app

# 3. Procfile erstellen (python-backend/Procfile)
web: python main.py

# 4. Deployment
git push heroku main

# 5. Zugriff
# https://job-mining-app.herokuapp.com
```

---

## 🔧 WICHTIGE PORTS

| Service | Port | URL |
|---------|------|-----|
| FastAPI (Python) | 5000 | http://localhost:5000 |
| Kotlin Spring Boot | 8080 | http://localhost:8080 |
| Dashboard Karte | 5000 | http://localhost:5000/dashboard/map |
| FastAPI Swagger | 5000 | http://localhost:5000/docs |
| Kotlin Swagger | 8080 | http://localhost:8080/swagger-ui/index.html |

---

## 📊 NEUE FEATURES (2025-12-27)

### Interaktive Karte mit Filtern
- **URL:** http://localhost:5000/dashboard/map
- **Filter:** Jahr (2020-2025), Beruf (5 Rollen)
- **Kompetenzen:** Top-10 Skills pro Beruf
- **Visualisierung:** X-Symbol-Overlay (Dichte-basiert)

**API-Beispiel:**
```bash
# Geo-Daten mit Filtern
curl "http://localhost:5000/api/dashboard/geo-heatmap?year=2025&role=Data%20Scientist"

# Response:
{
  "locations": [
    {"location": "Berlin", "lat": 52.52, "lon": 13.40, "count": 1260, "color": "#e74c3c"},
    ...
  ],
  "competences": [
    {"skill": "Python", "count": 2100},
    {"skill": "Machine Learning", "count": 1680},
    ...
  ]
}
```

---

## 🆘 TROUBLESHOOTING

### Port bereits belegt
```bash
# Linux/Mac
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### spaCy Modell fehlt
```bash
python -m spacy download de_core_news_md
# Falls nicht gefunden:
pip install spacy[lookups]
```

### Docker Build Fehler
```bash
# Cache löschen
docker-compose down --volumes
docker system prune -a

# Neu bauen
docker-compose build --no-cache
docker-compose up -d
```

### Import-Fehler (Python)
```bash
# Sicherstellen: Du bist in python-backend/
cd python-backend
export PYTHONPATH=$(pwd)
python main.py
```

---

## 📝 ZUSAMMENFASSUNG

| Szenario | Setup-Zeit | Schwierigkeit | Best Use Case |
|----------|-----------|--------------|---------------|
| **A) Lokal** | 5 Min | ⭐ Einfach | Entwicklung, Testing |
| **B) Docker** | 10 Min | ⭐⭐ Mittel | Server, Staging |
| **C) Cloud** | 15-30 Min | ⭐⭐⭐ Komplex | Production, Skalierung |

---

## 🎯 QUICK START (Empfohlen)

```bash
# 1. Setup
git clone <repo>
cd job-mining-kotlin-python
python3 -m venv venv && source venv/bin/activate
pip install -r python-backend/requirements.txt
python -m spacy download de_core_news_md

# 2. Starten
cd python-backend && python main.py

# 3. Browser
open http://localhost:5000/dashboard/map
```

**Fertig!** 🎉

---

**Support:**
- API-Docs: http://localhost:5000/docs
- Swagger (Kotlin): http://localhost:8080/swagger-ui/index.html
- GitHub Issues: [Link to repo]
