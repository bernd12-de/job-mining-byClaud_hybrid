# Domain-Generierung für Level 4 & 5

## Übersicht

Das Script `generate_domains.py` extrahiert automatisch Fachbegriffe aus PDF-Dokumenten und erstellt Domain-JSON-Dateien für das 7-Ebenen-Mapping.

## Verwendung

### 1. PDFs platzieren

```bash
# Level 4: Fachbücher
python-backend/data/source_pdfs/fachbuecher/
├── Gharbi_Softwarearchitektur_4A.pdf
├── Wolff_Microservices.pdf
├── 978-3-658-39649-7.pdf
└── 978-3-662-70277-2.pdf

# Level 5: Modulhandbücher
python-backend/data/source_pdfs/modulhandbuecher/
├── MHB_WI2_M_Sc_PO_2019_Stand_05_04_22.pdf
└── BA_fachspez.-Anhang-PO_20250605.pdf
```

### 2. Script ausführen

```bash
cd python-backend
python generate_domains.py
```

### 3. Ausgabe

Das Script erstellt zwei JSON-Dateien:

```bash
data/job_domains/
├── fachbuch_domain.json      # Level 4 (~5000 Skills)
└── academia_domain.json       # Level 5 (~2000 Skills)
```

## Format der generierten Domains

```json
{
  "domain": "Fachbuch Domain (Softwarearchitektur & Microservices)",
  "level": 4,
  "source": "Generated from PDFs",
  "competences": [
    {
      "name": "Microservices",
      "category": "Extracted",
      "type": "skill",
      "level": 4
    },
    {
      "name": "Softwarearchitektur",
      "category": "Extracted",
      "type": "skill",
      "level": 4
    }
  ]
}
```

## Extraktions-Logik

### 1. Pattern Matching
- Regex: `\b[A-ZÄÖÜ][a-zäöüß-]{3,25}\b`
- Findet: Substantive und Komposita mit Großbuchstaben am Anfang
- Beispiele: "Microservices", "Softwarearchitektur", "Modulhandbuch"

### 2. Filterung
- Mindestlänge: 4 Zeichen
- Keine reinen Großbuchstaben (Abkürzungen)
- Deduplizierung (Set)

### 3. Limitierung
- Maximal 5000 Skills pro Domain
- Alphabetisch sortiert

## Aktuelle Statistik

Nach der Generierung:

```
📊 Domain-Statistik:
   Custom Domains: 7
   Fachbuch Skills (Level 4): 13.464
   Academia Skills (Level 5): 2.043
   ESCO Skills: 13.933
```

### Quellen

**Level 4 - Fachbücher:**
- Gharbi: Softwarearchitektur (4. Auflage)
- Wolff: Microservices
- Springer-Fachbücher zu Software Engineering

**Level 5 - Academia:**
- Modulhandbuch Wirtschaftsinformatik Master
- Bachelor-Fachspezifischer Anhang

## Integration im Repository

Die Domains werden automatisch vom `HybridCompetenceRepository` geladen:

```python
repo = HybridCompetenceRepository(rule_client=None)

# Level-Tests
print(repo.get_level("microservices"))        # → 4
print(repo.get_level("softwarearchitektur"))  # → 5
print(repo.get_level("modulhandbuch"))        # → 5
```

### Priorität

```
Academia (5) > Fachbuch (4) > ESCO Digital (3) > ESCO Standard (2) > Discovery (1)
```

## Wartung

### Neue Fachbücher hinzufügen

1. PDF in `data/source_pdfs/fachbuecher/` kopieren
2. Script erneut ausführen: `python generate_domains.py`
3. Bestehende Domain wird überschrieben und aktualisiert

### Neue Modulhandbücher hinzufügen

1. PDF in `data/source_pdfs/modulhandbuecher/` kopieren
2. Script erneut ausführen: `python generate_domains.py`
3. Bestehende Domain wird überschrieben und aktualisiert

## Qualitätskontrolle

### Manuelle Prüfung

```bash
# Top 20 Skills aus Fachbuch-Domain
cat data/job_domains/fachbuch_domain.json | jq '.competences[0:20] | .[].name'

# Top 20 Skills aus Academia-Domain
cat data/job_domains/academia_domain.json | jq '.competences[0:20] | .[].name'
```

### Test-Ausführung

```bash
cd python-backend
python -m pytest tests/test_repository_levels.py -v
```

## Bekannte Einschränkungen

1. **Nur deutsche Begriffe:** Pattern erkennt nur deutsche Substantive
2. **Keine Kontextanalyse:** Skills ohne semantische Validierung
3. **Rauschen:** Eigennamen und nicht-fachliche Begriffe werden mitextrahiert
4. **Keine Duplikats-Bereinigung über Domains:** Gleiche Skills können in mehreren Domains erscheinen

## Zukünftige Verbesserungen

- [ ] NLP-basierte Extraktion mit spaCy
- [ ] Semantic Filtering gegen ESCO-Ontologie
- [ ] Multi-Language Support (EN/DE)
- [ ] Automatische Kategorie-Erkennung
- [ ] Confidence Scoring basierend auf Häufigkeit
