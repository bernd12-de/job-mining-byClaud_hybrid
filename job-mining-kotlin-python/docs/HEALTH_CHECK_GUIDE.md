# 🔍 API Health-Check System - Betriebsdokumentation

## 📋 Übersicht

Das **API Health-Check System** validiert beim Startup und kontinuierlich zur Laufzeit, dass alle 28 registrierten API-Endpoints erreichbar sind. Wenn Endpoints **LOST** gehen (nicht mehr erreichbar), wird das System **sofort erkannt und gemeldet**.

---

## 🎯 Ziel

**Problem:** Endpoints gehen oft verloren während der Entwicklung und sind schwer zu tracken.

**Lösung:** 
1. ✅ Zentrale Registrierung aller Endpoints (`.api-endpoints-registry`)
2. ✅ Automatische Validierung beim Startup (`api-health-check.sh`)
3. ✅ Kontinuierliche Überwachung zur Laufzeit (`api-health-monitor.sh`)
4. ✅ Strukturiertes Logging und Alerting

---

## 🚀 Startup mit Health-Check

### Option 1: Vollautomatischer Start mit Validierung

```bash
./startup-with-health-check.sh
```

**Was passiert:**
1. 🐳 Startet alle Docker Services (`docker-compose up -d`)
2. ⏳ Wartet auf Service-Startup (ca. 10-30s)
3. 🔍 Führt Health-Check durch (validiert alle 28 Endpoints)
4. 📊 Zeigt Status Dashboard mit Access-Links

**Erfolgreicher Output:**
```
✅ SYSTEM BEREIT

📊 Dashboard:        http://localhost:8501
🔌 Kotlin API:       http://localhost:8080
🐍 Python Backend:   http://localhost:8000
📚 Swagger UI:       http://localhost:8080/swagger-ui.html
```

**Fehlerfall:**
```
❌ FEHLER: Einige Endpoints sind LOST

🔧 Troubleshooting:
  1. Zeige aktuelle Container: docker ps
  2. Zeige Logs:               docker-compose logs -f
  3. Health-Report:           api-health-report-2025-12-27-08:01:38.txt
```

---

## 🔍 Health-Check Skripte

### 1. `api-health-check.sh` (Einmalige Validierung)

**Zweck:** Einmalige Validierung aller Endpoints beim Startup

**Verwendung:**
```bash
./api-health-check.sh
```

**Output-Formate:**

**Konsole (Echtzeit):**
```
[2025-12-27 08:15:42] ⏳ Warte auf Kotlin API (8080)...
[OK] Kotlin API ist READY
[2025-12-27 08:15:45] 🔍 Validiere alle registrierten Endpoints...

✅ 28/28 ENDPOINTS ERREICHBAR
✅ Alle Systeme operativ
```

**Oder bei Problemen:**
```
❌ 5/28 ENDPOINTS LOST (nicht erreichbar)

LOST ENDPOINTS:
  - POST /batch-process (python)
  - GET /reports/dashboard-metrics (python)
  - POST /api/v1/jobs/upload (kotlin)
  - ...
```

**Output-Dateien:**
- `api-health-check.log` - Strukturiertes Log aller Checks
- `api-health-report-YYYY-MM-DD-HH:MM:SS.txt` - Timestamped Report

**Exit-Codes:**
- `0` = Alle 28 Endpoints OK
- `1` = Mindestens ein Endpoint DOWN

### 2. `api-health-monitor.sh` (Kontinuierliche Überwachung)

**Zweck:** Läuft im Hintergrund und überwacht Endpoints kontinuierlich

**Verwendung:**
```bash
# Einmalige Überwachung (Check alle 5 Min)
./api-health-monitor.sh

# Custom Intervall (Check alle 30 Sekunden)
./api-health-monitor.sh 30

# Mit Alert-Schwelle (Alert nach 3 Fehlern)
./api-health-monitor.sh 60 3
```

**Monitoring-Parameter:**
- **CHECK_INTERVAL** (Standard: 300s = 5 Minuten)
  - Zeit zwischen Health-Checks
  - Beispiel: `60` = prüfe jede Minute
- **ALERT_THRESHOLD** (Standard: 2)
  - Nach wie vielen aufeinanderfolgenden Fehlern Alert senden
  - Beispiel: `1` = sofort alert bei erstem Fehler

**Output-Dateien:**
- `api-health-monitor.log` - Alle Check-Ergebnisse mit Timestamp
- `api-health-alerts.log` - Alert-Notifications (wenn Probleme auftreten)

**Beispiel Überwachungs-Ausgabe:**
```
[1] Check @ 2025-12-27 08:15:45
✅ All systems operational

[2] Check @ 2025-12-27 08:20:45
✅ All systems operational

[3] Check @ 2025-12-27 08:25:45
❌ Issues detected

🚨 ALERT 🚨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subject: API Health Check Failing
Time:    2025-12-27 08:25:45
Details: Health check has failed 1 times consecutively...
```

---

## 📋 Endpoint Registry

**Datei:** `.api-endpoints-registry`

**Format:** `METHOD|PATH|DESCRIPTION|SERVICE` (pipe-separated)

**Gesamtanzahl:** 28 Endpoints
- 18 Kotlin Endpoints (8080)
- 10 Python Endpoints (8000)

**Auszug:**
```
POST|/api/v1/jobs/upload|Upload Job File|kotlin
POST|/api/v1/jobs/scrape|Scrape Job from URL|kotlin
GET|/api/v1/jobs|List all jobs|kotlin
GET|/api/v1/jobs/reports/dashboard-metrics|Get Dashboard Metrics|kotlin
POST|/analyse/file|Analyze Job File|python
POST|/analyse/scrape-url|Scrape and Analyze URL|python
POST|/batch-process|Batch Process Jobs|python
GET|/system/status|Get System Status|python
```

**Verwendung:**
- Quelle für Health-Check Validierungen
- Dokumentation für Entwickler
- Versioning für API-Änderungen

---

## 🐳 Docker Integration

### Docker-Compose Service: `api-health-check`

**Konfiguration in `docker-compose.yml`:**
```yaml
api-health-check:
  image: alpine:latest
  command: >
    sh -c "
    apk add --no-cache bash curl &&
    cp /mnt/check.sh /check.sh &&
    chmod +x /check.sh &&
    /check.sh
    "
  volumes:
    - .:/mnt
    - ./api-health-check.sh:/mnt/check.sh:ro
  depends_on:
    - kotlin-api
    - python-backend
  healthcheck:
    test: ["CMD", "bash", "/check.sh"]
    interval: 60s
    timeout: 30s
    retries: 1
```

**Besonderheiten:**
- ✅ Startet automatisch mit `docker-compose up`
- ✅ Wartet auf abhängige Services (kotlin-api, python-backend)
- ✅ Health-Check läuft nach Service-Startup
- ✅ Integegriert in Docker-Health-System

---

## 📊 Logs und Reports

### Log-Dateien

| Datei | Zweck | Aktualisierung |
|-------|-------|----------------|
| `api-health-check.log` | Health-Check Results | Jeder Check |
| `api-health-monitor.log` | Monitoring Session Log | Jede Minute (bei Monitoring) |
| `api-health-alerts.log` | Alert-Benachrichtigungen | Bei Problemen |
| `api-health-report-*.txt` | Timestamped Full Report | Nach jedem Check |

### Report-Format

**Beispiel:** `api-health-report-2025-12-27-08:15:42.txt`

```
════════════════════════════════════════════════════════════════════════════════

✅ 28/28 ENDPOINTS ERREICHBAR

Services Status:
  ✅ kotlin:8080   - READY   (5 endpoints checked)
  ✅ python:8000   - READY   (3 endpoints checked)
  ✅ postgres:5432 - READY

═════════════════════════════════════════════════════════════════════════════════

Checked Endpoints:
  ✅ POST /api/v1/jobs/upload
  ✅ POST /api/v1/jobs/scrape
  ✅ GET /api/v1/jobs
  ✅ GET /api/v1/jobs/reports/dashboard-metrics
  ✅ POST /analyse/file
  ... (weitere 23 Endpoints)

═════════════════════════════════════════════════════════════════════════════════
Report Generated: 2025-12-27 08:15:42
Check Duration: 8.523 seconds
```

---

## 🔧 Troubleshooting

### Fall 1: "Python Backend ist NICHT ERREICHBAR"

```
❌ 10/10 Python Endpoints LOST

Lösung:
  1. Prüfe Docker-Container: docker ps | grep python
  2. Zeige Logs: docker logs python-backend
  3. Prüfe Port: netstat -an | grep 8000
  4. Restarte: docker-compose restart python-backend
```

### Fall 2: "Kotlin API LOST nach Update"

```
❌ 18/18 Kotlin Endpoints LOST

Lösung:
  1. Check Build-Fehler: docker logs kotlin-api | tail -50
  2. Prüfe Springdoc Version: grep springdoc build.gradle.kts
  3. Rebuild: docker-compose up --build kotlin-api
  4. Health-Check erneut: ./api-health-check.sh
```

### Fall 3: Health-Check selbst fehlgeschlagen

```
❌ Health-Check Script Fehler

Lösung:
  1. Script-Berechtigungen: chmod +x api-health-check.sh
  2. Registry prüfen: cat .api-endpoints-registry | wc -l (sollte 28 sein)
  3. Bash verfügbar: which bash
  4. Curl verfügbar: which curl
```

---

## 📈 Best Practices

### 1. Automatischer Start
```bash
# In Production: Immer mit Health-Check starten
./startup-with-health-check.sh
# ↓
# Startet Docker + validiert alle Endpoints
# ↓
# Nur bei Erfolg (Status ✅) ist System bereit
```

### 2. Kontinuierliche Überwachung
```bash
# In Background laufen lassen
./api-health-monitor.sh 300 2 &

# Logs beobachten
tail -f api-health-monitor.log
tail -f api-health-alerts.log
```

### 3. Bei Code-Changes
```bash
# Nach API-Änderungen Health-Check durchführen
docker-compose restart kotlin-api
./api-health-check.sh

# Falls Endpoints geändert: Registry aktualisieren
nano .api-endpoints-registry
```

### 4. Monitoring Setup
```bash
# Terminal 1: Health-Monitor laufen lassen
./api-health-monitor.sh

# Terminal 2: Log-Stream anschauen
watch -n 5 'tail -20 api-health-monitor.log'

# Terminal 3: Alerts anschauen
watch -n 5 'tail -20 api-health-alerts.log'
```

---

## 📚 Zusammenfassung der Dateien

| Datei | Typ | Zweck |
|-------|-----|-------|
| `startup-with-health-check.sh` | Bash | Vollautomatischer Start mit Validierung |
| `api-health-check.sh` | Bash | Einmalige Health-Check Validierung |
| `api-health-monitor.sh` | Bash | Kontinuierliche Überwachung & Alerting |
| `.api-endpoints-registry` | Text | Zentrale Registry aller 28 Endpoints |
| `api-health-check.log` | Log | Health-Check Logs |
| `api-health-monitor.log` | Log | Monitoring Session Logs |
| `api-health-alerts.log` | Log | Alert-Benachrichtigungen |
| `api-health-report-*.txt` | Report | Timestamped Full Reports |

---

## ✅ Validierung

System ist produktionsreif wenn:

- [x] `api-health-check.sh` ist ausführbar
- [x] `.api-endpoints-registry` enthält 28 Endpoints
- [x] `startup-with-health-check.sh` läuft ohne Fehler
- [x] Health-Check validiert alle Endpoints erfolgreich
- [x] Docker-Compose Service `api-health-check` ist konfiguriert
- [x] Monitoring funktioniert und loggt korrekt

---

## 🚀 Produktions-Checklist

Vor Production-Deployment:

```bash
# 1. Health-Check testen
./api-health-check.sh

# 2. Startup-Skript testen
./startup-with-health-check.sh

# 3. Monitoring testen (30 Sekunden)
timeout 30 ./api-health-monitor.sh 5 1 || true

# 4. Logs prüfen
cat api-health-check.log | tail -30
cat api-health-monitor.log | tail -30

# 5. Docker Status
docker-compose ps
```

---

**Version:** 1.0  
**Erstellt:** 2025-12-27  
**Status:** ✅ Produktionsreif
