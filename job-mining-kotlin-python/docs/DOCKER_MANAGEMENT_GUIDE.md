# 🐳 Docker Management & Logging Guide

## ✅ Fertig implementiert: 3️⃣ DOCKER-LOGGER UMLEITEN

### 📜 Live-Logs im Terminal

**Option 1: Interaktives Management-Menü** (empfohlen)
```bash
./docker-manager.sh
```

Funktionen:
- 📊 Container Status anzeigen
- 📜 Live-Logs streamen (alle oder einzelne Services)
- 🔄 Container einzeln oder alle neustarten
- 🏗️ Container neu bauen
- 🧹 Logs löschen und neu starten

**Option 2: Live-Log-Streaming-Script**
```bash
# Alle Container
./docker-logs-live.sh

# Nur Python Backend
./docker-logs-live.sh python-backend

# Nur Kotlin API
./docker-logs-live.sh kotlin-api

# Nur Database
./docker-logs-live.sh jobmining-db
```

**Option 3: Direkte Docker-Befehle**
```bash
# Live-Streaming (alle Services, farbcodiert)
docker compose logs -f --tail=50

# Nur Python Backend (letzte 200 Zeilen)
docker compose logs -f --tail=200 python-backend

# Nur Fehler filtern
docker compose logs python-backend | grep -i error

# Container neustarten
docker compose restart python-backend
docker compose restart kotlin-api
```

---

## ✅ Fertig implementiert: 6️⃣ "PER KNOPF" RESTART

### 🌐 Web-Dashboard mit Passwortschutz

**URL:** http://localhost:8501 (oder Codespaces-Port 8501)

**Features:**
- 🔐 **Passwort-geschützt** (Standard: `admin123`)
- 🔄 **Restart-Buttons** für jeden Container
- 📜 **Live-Logs-Viewer** mit einstellbarer Zeilenzahl
- 📊 **Container-Status** Echtzeit-Überwachung
- 📈 **Analytics** Dashboard (Metrics, Charts, Reports)

**Verwendung:**
1. Öffne http://localhost:8501
2. Sidebar → Admin Panel
3. Passwort eingeben: `admin123`
4. Service auswählen und "🔄 Restart" klicken

**Passwort ändern:**
```bash
# In docker-compose.yml oder Environment Variable setzen:
export DASHBOARD_ADMIN_PASSWORD="mein_sicheres_passwort"
```

---

## 🔧 Quick Reference

### Container Status
```bash
docker compose ps
```

### Container Logs
```bash
# Letzte 50 Zeilen
docker compose logs --tail=50 python-backend

# Live-Streaming
docker compose logs -f python-backend

# Alle Container gleichzeitig
docker compose logs -f
```

### Container Neustarten
```bash
# Einzelner Service
docker compose restart python-backend

# Alle Services
docker compose restart

# Mit Rebuild
docker compose up -d --build python-backend
```

### Container Stoppen/Starten
```bash
# Stoppen
docker compose down

# Starten
docker compose up -d

# Neu bauen und starten
docker compose up -d --build
```

### Logs löschen
```bash
# Container stoppen und Volumes löschen
docker compose down -v

# Neu starten
docker compose up -d
```

---

## 🔐 Sicherheit

**Wichtig:** Das Standard-Passwort `admin123` ist **nur für Entwicklung**!

Für Produktion:
1. Setze `DASHBOARD_ADMIN_PASSWORD` Environment Variable
2. Nutze einen starken Passwort-Generator
3. Aktiviere HTTPS
4. Nutze OAuth/LDAP für echte Authentifizierung

---

## 📦 Verfügbare Services

| Service          | Port  | Restart-Name       | Beschreibung           |
|------------------|-------|-------------------|------------------------|
| Python Backend   | 8000  | `python-backend`  | FastAPI NLP Service    |
| Kotlin API       | 8080  | `kotlin-api`      | Spring Boot Backend    |
| PostgreSQL       | 5432  | `jobmining-db`    | Datenbank              |
| Streamlit        | 8501  | `streamlit`       | Dashboard & Management |

---

## 🐛 Troubleshooting

**Problem: "Permission denied" beim Script-Ausführen**
```bash
chmod +x docker-manager.sh docker-logs-live.sh
```

**Problem: "Container not found"**
```bash
# Prüfe ob Docker läuft
docker compose ps

# Starte alle Container
docker compose up -d
```

**Problem: Streamlit zeigt keine Logs**
```bash
# Prüfe ob Docker Socket erreichbar ist
docker ps

# Streamlit Container hat Zugriff auf Docker Socket (in docker-compose.yml)
```

**Problem: Passwort funktioniert nicht**
```bash
# Standard-Passwort ist: admin123
# Oder setze eigenes:
export DASHBOARD_ADMIN_PASSWORD="mein_passwort"
docker compose restart streamlit
```

---

## 📚 Weitere Ressourcen

- [Docker Compose Dokumentation](https://docs.docker.com/compose/)
- [Streamlit Dokumentation](https://docs.streamlit.io/)
- API Endpoints: [API_ENDPOINTS.md](API_ENDPOINTS.md)
- Health Check: [HEALTH_CHECK_GUIDE.md](HEALTH_CHECK_GUIDE.md)
