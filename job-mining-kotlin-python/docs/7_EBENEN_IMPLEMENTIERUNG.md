# 7-Ebenen-Mapping: Vollständige Implementierung

## Übersicht

Das 7-Ebenen-Konzept ist jetzt vollständig im `HybridCompetenceRepository` implementiert. Es ermöglicht eine hierarchische Klassifizierung von Skills basierend auf ihrer Herkunft und Spezifität.

## Die 7 Ebenen im Detail

### **Level 7: Zeitreihen & Validierung** ⏰
**Status:** Konzeptionell erwähnt, nicht implementiert

Zukünftige Erweiterung für:
- Historische Trendanalyse
- Validierung über Zeit
- Prognosen

---

### **Level 6: Segmentierung & Kontext** 🎯
**Status:** Patterns vorhanden, nicht als numerischer Level

Erkannte Patterns (in MetadataExtractor):
- `TASK_PATTERN`: Tätigkeiten/Aufgaben
- `TOOL_PATTERN`: Werkzeuge/Software
- `METHOD_PATTERN`: Methoden/Frameworks

---

### **Level 5: Academia (Modulhandbücher)** 🎓
**Status:** ✅ Vollständig implementiert

**Priorität:** HÖCHSTE

**Quelle:** Akademische Domänen aus Modulhandbüchern

**Implementierung:**
```python
# Automatische Erkennung
if 'modulhandbuch' in path or 'academia' in path:
    level = 5

# Lookup
if term in self._academia_skills:
    return 5
```

**Beispiel-Skills:**
- Deep Learning
- Neural Networks
- Quantentheorie

---

### **Level 4: Fachbücher** 📚
**Status:** ✅ Vollständig implementiert

**Quelle:** Fach-spezifische Domänen aus Fachliteratur

**Implementierung:**
```python
# Automatische Erkennung
if 'fachbuch' in path or 'fachbuecher' in path:
    level = 4

# Lookup
if term in self._fachbuch_skills:
    return 4
```

**Beispiel-Skills:**
- Agiles Projektmanagement
- Stakeholder Management
- Microservices Architecture

---

### **Level 3: ESCO Digital Skills** 💻
**Status:** ✅ Vollständig implementiert

**Quelle:** ESCO Skills mit Digital-Flag ODER Keyword-Heuristik

**Implementierung:**
```python
# 1) ESCO Digital Collection Flag
if esco_data[term].get('is_digital', False):
    return 3

# 2) Keyword-basierte Heuristik mit Wortgrenzen
digital_keywords = [
    'software', 'digital', 'programm', 'python', 'java',
    'cloud', 'machine learning', 'api', 'database', ...
]

# 3) Regex-basierter Match mit \b Wortgrenzen
```

**Beispiel-Skills:**
- Python Programming
- Machine Learning
- Cloud Computing
- SAP ERP
- JavaScript

---

### **Level 2: ESCO Standard** 🌍
**Status:** ✅ Vollständig implementiert

**Quelle:** Standard ESCO-Skills ohne Digital-Flag

**Default-Level** für:
- Bekannte ESCO Skills
- Unbekannte Skills (Fallback)

**Beispiel-Skills:**
- Teamarbeit
- Kommunikation
- Projektmanagement (allgemein)

---

### **Level 1: Discovery** 🔍
**Status:** ✅ Implementiert in DiscoveryExtractor

**Quelle:** Neue, unbekannte Skills direkt aus PDFs

**Verwendung:**
```python
CompetenceDTO(
    name="Neue unbekannte Kompetenz",
    level=1,
    is_discovery=True
)
```

---

## Prioritätshierarchie

```
Academia (5) > Fachbuch (4) > ESCO Digital (3) > ESCO Standard (2) > Discovery (1)
```

Die `get_level()` Methode durchläuft diese Prüfungen in dieser Reihenfolge:

```python
def get_level(self, term: str) -> int:
    # 1. Academia Check
    if term in self._academia_skills:
        return 5
    
    # 2. Fachbuch Check
    if term in self._fachbuch_skills:
        return 4
    
    # 3. ESCO mit Digital-Flag
    if term in self.esco_data:
        if esco_data[term]['is_digital']:
            return 3
        return esco_data[term].get('level', 2)
    
    # 4. Custom Domains
    for domain in self.custom_domains:
        if match:
            return domain['level']
    
    # 5. Heuristik & Fallback
    return 2  # Default
```

---

## Implementierte Methoden

### `get_level(term: str) -> int`
Bestimmt das Level eines Skills nach Priorität.

### `is_digital_skill(term: str) -> bool`
Prüft, ob ein Skill digital ist (Level 3 relevant).

**Heuristiken:**
1. ESCO Digital Collection Flag
2. Keyword-Match mit Wortgrenzen (regex `\b`)
3. Substring-Match in bekannten digitalen Skills

### `_load_local_domains_v2()`
Lädt Custom Domains aus JSON-Dateien:
- `data/job_domains/`
- `data/fachbuecher/`
- `data/modulhandbuecher/`

**Auto-Detection:**
- Pfad enthält "fachbuch" → Level 4
- Pfad enthält "modulhandbuch" oder "academia" → Level 5

### `_sync_legacy_sets()`
Synchronisiert Legacy Sets für Backward-Compatibility:
- `_fachbuch_skills` (Level 4)
- `_academia_skills` (Level 5)

### `_build_esco_index()`
Baut Index `self.esco_data` auf:
```python
{
    "python programming": {
        "uri": "...",
        "preferredLabel": "Python Programming",
        "level": 2,
        "is_digital": True,
        "source_domain": "ESCO"
    }
}
```

---

## Datenquellen & Pfade

### ESCO Skills (Level 2/3)
- **API:** `http://kotlin-api:8080/api/v1/rules/esco-full`
- **Fallback:** `data/esco/skills_de.csv`
- **Anzahl:** ~13.938 Skills (lokal)

### Custom Skills
- **Datei:** `data/custom_skills_extended.json`

### Custom Domains (Level 4/5)
- **Pfad:** `data/job_domains/`
- **Format:** JSON mit `domain`, `level`, `competences[]`
- **Auto-Level:** Basierend auf Ordnername

**Beispiel Domain JSON:**
```json
{
  "domain": "Künstliche Intelligenz",
  "level": 5,
  "competences": [
    {"name": "Deep Learning", "level": 5},
    {"name": "Neural Networks", "level": 5}
  ]
}
```

---

## Tests

Alle Level-Tests sind grün ✅:

```bash
cd python-backend
python -m pytest tests/test_repository_levels.py -v
```

**Test-Coverage:**
- ✅ `test_get_level_priority` - Academia > Fachbuch Priorität
- ✅ `test_is_digital_skill_and_esco_index` - Digital Flag & Index
- ✅ `test_digital_skill_keyword_heuristic` - Keyword-Erkennung
- ✅ `test_level_hierarchy_with_digital_flag` - Gesamte Hierarchie
- ✅ `test_unknown_skill_default_level` - Fallback Level 2

---

## Verwendung im Code

### In Extractors (z.B. MetadataExtractor)

```python
level = self.repository.get_level(competence_name)
is_digital = self.repository.is_digital_skill(competence_name)

dto = CompetenceDTO(
    name=competence_name,
    level=level,
    is_digital=is_digital,
    source="metadata"
)
```

### In Analytics/Reporting

```python
# Gruppierung nach Level
competences_by_level = defaultdict(list)
for comp in all_competences:
    level = repo.get_level(comp.name)
    competences_by_level[level].append(comp)

# Statistik
print(f"Academia Skills (L5): {len(competences_by_level[5])}")
print(f"Fachbuch Skills (L4): {len(competences_by_level[4])}")
print(f"Digital Skills (L3): {len(competences_by_level[3])}")
```

### Im Dashboard

```python
# Filter für digitale Skills
digital_skills = [
    s for s in skills 
    if repo.is_digital_skill(s.name)
]

# Visualisierung nach Level
level_distribution = {
    "Level 5 (Academia)": len([s for s in skills if repo.get_level(s.name) == 5]),
    "Level 4 (Fachbuch)": len([s for s in skills if repo.get_level(s.name) == 4]),
    "Level 3 (Digital)": len([s for s in skills if repo.get_level(s.name) == 3]),
    "Level 2 (Standard)": len([s for s in skills if repo.get_level(s.name) == 2]),
}
```

---

## Performance & Optimierungen

### Index-basierte Lookups
- `self.esco_data`: Dict für O(1) Lookup
- `self._fachbuch_skills`: Set für O(1) Membership
- `self._academia_skills`: Set für O(1) Membership

### Lazy Loading
- Domains nur beim Init geladen
- ESCO API mit Fallback auf lokale CSV

### Caching
- Alle Daten im Memory
- Kein wiederholtes Laden während Runtime

---

## Bekannte Limitierungen

1. **Level 6/7 nicht implementiert:** Segmentierung ist nur als Pattern vorhanden
2. **Digital-Heuristik:** Keyword-basiert, nicht ML-gestützt
3. **Keine dynamische Domain-Updates:** Domains werden nur beim Init geladen
4. **Substring-Matching:** Kann zu False Positives führen bei sehr kurzen Terms

---

## Nächste Schritte

### Kurzfristig
- [ ] Integration in Job Upload Pipeline testen
- [ ] Dashboard-Visualisierung für Level-Distribution
- [ ] Performance-Profiling bei großen Datasets

### Mittelfristig
- [ ] Level 6: Segmentierung als numerisches Level
- [ ] ML-basierte Digital-Skill-Erkennung
- [ ] Dynamisches Domain-Reloading

### Langfristig
- [ ] Level 7: Zeitreihenanalyse
- [ ] Multi-Language Support für Digital-Keywords
- [ ] Graph-basierte Skill-Beziehungen

---

## Änderungshistorie

**2025-12-27:**
- ✅ Vollständige Implementierung Level 1-5
- ✅ `get_level()` mit Prioritätshierarchie
- ✅ `is_digital_skill()` mit Regex-Heuristik
- ✅ `_load_local_domains_v2()` mit Auto-Level-Detection
- ✅ `_sync_legacy_sets()` mit Logging
- ✅ Unit-Tests für alle Level
- ✅ Dokumentation

---

## Referenzen

- [7_ebenen_summary.md](konzept-ideen/7_ebenen_summary.md) - Ursprüngliches Konzept
- [hybrid_competence_repository.py](python-backend/app/infrastructure/repositories/hybrid_competence_repository.py) - Implementierung
- [test_repository_levels.py](python-backend/tests/test_repository_levels.py) - Tests
