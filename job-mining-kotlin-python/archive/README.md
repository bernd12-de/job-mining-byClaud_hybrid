# 📦 Archiv - Historische Dateien

Dieses Verzeichnis enthält historische Code- und Dokumentations-Versionen, die nicht mehr im aktiven Produktivbetrieb verwendet werden, aber aus historischen und Referenz-Gründen aufbewahrt werden.

## 📁 Struktur

### `v2-prototype/` - Version 2.0 Prototyp (Dezember 2024/2025)

**Status:** 🟡 Experimenteller Prototyp, nicht produktiv

Ein Versuch, das System mit Clean Architecture und Dataclasses neu zu schreiben. Wurde nicht vollständig integriert, da die bestehende Pydantic-basierte Lösung produktiver war.

#### Enthaltene Dateien:
- `main_v2.py` - Standalone Demo-Script für V2-Pipeline
- `models_v2.py` - Domain Models mit Dataclasses (statt Pydantic)
- `docker-compose.v2.yml` - Docker-Setup für V2-Prototyp
- `Dockerfile.v2` - Multi-Stage Build für V2

#### Warum archiviert?
- ❌ Dataclasses weniger geeignet als Pydantic für FastAPI
- ❌ Keine automatische JSON-Serialisierung
- ❌ Keine Field-Validierung
- ❌ Zusätzlicher Konvertierungs-Overhead
- ✅ Aktuelle Lösung ist production-ready und wartbarer

#### Gute Ideen aus V2 (bereits übernommen):
- ✅ Immutability-Konzepte
- ✅ Domain-Methoden in Models
- ✅ Fehlerbehandlung

---

### `v2-documentation/` - V2.0 Dokumentation

**Status:** 🟡 Historische Referenz

Umfangreiche Dokumentation für den V2.0-Prototyp. Enthält wertvolle Erkenntnisse über Systemarchitektur und Troubleshooting.

#### Enthaltene Dateien:
- `QUICKSTART_V2.0.md` - Feature-Overview der V2-Architektur
- `SETUP_V2.0.md` - Setup & Troubleshooting Guide
- `V2_STATUS_REPORT.md` - Migrations-Bericht und Bug-Fixes
- `VALIDATION_CHECKLIST.md` - Test-Checkliste für V2
- `V2_QUICK_REFERENCE.sh` - Shell-Script mit V2-Befehlen

#### Warum archiviert?
- ❌ Bezieht sich auf nicht-produktive Dateien
- ❌ Verwirrt neue Entwickler ("Warum zwei Versionen?")
- ✅ Wertvoll als historische Referenz
- ✅ Enthält gute Troubleshooting-Tipps (können in Haupt-Docs übernommen werden)

---

## 🚀 Produktiv-System (aktuell)

**Das läuft aktuell in Production:**

```
python-backend/
├── main.py                    ✅ FastAPI Server (Port 8000)
├── dashboard_app.py           ✅ Streamlit Dashboard
├── app/
    ├── domain/models.py       ✅ Pydantic Models (PRODUKTIV)
    ├── application/           ✅ Services & Workflow
    ├── infrastructure/        ✅ Extraktoren & Repositories
```

**Starten:**
```bash
# Haupt-API
cd python-backend && uvicorn main:app --reload

# Dashboard
streamlit run dashboard_app.py

# Docker
docker-compose up --build
```

---

## 🔄 V2-Prototyp reaktivieren (optional)

Falls du den V2-Prototyp zu Testzwecken starten möchtest:

### Option 1: Standalone Demo
```bash
# Kopiere main_v2.py zurück
cp archive/v2-prototype/main_v2.py python-backend/
cp archive/v2-prototype/models_v2.py python-backend/app/core/

# Starte Demo
cd python-backend
python main_v2.py
```

### Option 2: Mit Docker
```bash
# Kopiere Docker-Files zurück
cp archive/v2-prototype/docker-compose.v2.yml .
cp archive/v2-prototype/Dockerfile.v2 .

# Starte
docker-compose -f docker-compose.v2.yml up --build
```

**⚠️ Hinweis:** Der V2-Prototyp ist nicht vollständig integriert mit dem Kotlin-Backend und hat keine API-Endpunkte!

---

## 📊 Lessons Learned aus V2

### Was gut war:
1. ✅ Klare Domain-Modell-Struktur
2. ✅ Immutability bei Core-Entities
3. ✅ Explizite Error-Handling-Patterns
4. ✅ Zeitreihen-Support eingebaut

### Was nicht funktionierte:
1. ❌ Dataclasses vs. Pydantic für Web-APIs
2. ❌ Manuelle Serialisierung/Validierung zu aufwändig
3. ❌ Zwei parallele Systeme = Verwirrung
4. ❌ Migration nie abgeschlossen

### Best Practices für zukünftige Refactorings:
- 🎯 Feature-Flags statt parallele Versionen
- 🎯 Inkrementelle Migration statt "Big Bang"
- 🎯 Pydantic für FastAPI-Projekte bevorzugen
- 🎯 Domain Logic kann auch in Pydantic Models

---

## 📖 Weitere Ressourcen

- [Haupt-README](../README.md) - Aktuelles System
- [DASHBOARD_GUIDE.md](../DASHBOARD_GUIDE.md) - Dashboard-Dokumentation
- [SYSTEM_SECURITY.md](../SYSTEM_SECURITY.md) - Fehlerbehandlung & Sicherheit

---

**Erstellt:** 27. Dezember 2025
**Archiviert von:** GitHub Copilot
**Grund:** Konsolidierung und Reduktion von Verwirrung
