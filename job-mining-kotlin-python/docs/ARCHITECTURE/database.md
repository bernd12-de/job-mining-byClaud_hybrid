# Datenbank-Schema - PostgreSQL

**DBMS:** PostgreSQL 14+ | **Port:** 5432

[← Zurück zu Architecture Index](./index.md)

---

## 📋 Tabellen-Übersicht

| Tabelle | Zweck | Records | Wichtige Spalten |
|---------|-------|---------|------------------|
| `job_postings` | Job-Anzeigen | ~1000-10000 | id, sourceUrl, filename, rawText, jobTitle, organization |
| `competences` | Extrahierte Skills | ~10000-50000 | id, originalTerm, escoLabel, escoUri, jobPostingId, confidenceScore |
| `esco_skills` | ESCO-Datensätze | ~17000 | id, escoUri, preferredLabel, skillType |
| `discovery_candidates` | Neue Skills | ~100-500 | id, skillTerm, count, firstSeen |
| `discovery_approved` | Genehmigte Skills | ~50-200 | skillId, approvedAt, approvedBy |
| `skill_blacklist` | Ignorierte Skills | ~10-50 | id, skillTerm, blacklistedAt |
| `domain_rules` | Custom Parsing-Regeln | ~10-50 | id, pattern, replacement, domain |
| `audit_log` | Änderungshistorie | ~10000+ | id, entityType, entityId, action, timestamp |

---

## 🔑 Tabellen-Details

### 1. job_postings
**Haupttabelle: Job-Anzeigen**

```sql
CREATE TABLE job_postings (
    id BIGSERIAL PRIMARY KEY,
    source_url VARCHAR(1000),                    -- Webseite (falls Web-Scrape)
    filename VARCHAR(255),                       -- Dateiname (falls PDF/DOCX)
    raw_text TEXT NOT NULL,                      -- Vollständiger Original-Text
    raw_text_hash VARCHAR(64) UNIQUE NOT NULL,   -- MD5/SHA256 für Idempotenz
    extracted_text TEXT,                         -- Bereinigter Text
    job_title VARCHAR(255),                      -- Berufsbezeichnung
    job_role VARCHAR(100),                       -- Kategorie (Sales, IT, etc.)
    organization VARCHAR(255),                   -- Arbeitgeber
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- Indices
CREATE INDEX idx_job_postings_source_url ON job_postings(source_url);
CREATE INDEX idx_job_postings_raw_text_hash ON job_postings(raw_text_hash);
CREATE INDEX idx_job_postings_organization ON job_postings(organization);
CREATE INDEX idx_job_postings_job_role ON job_postings(job_role);
CREATE INDEX idx_job_postings_created_at ON job_postings(created_at);
```

**Erklärung:**
- `raw_text_hash` - Verhindert Duplikate (Idempotenz)
- `job_role` - "Sales", "IT", "Marketing" (Ebene 6)
- `organization` - Firmenname (Ebene 5)
- Indices für schnelle Lookups

---

### 2. competences
**Extrahierte Skills pro Job**

```sql
CREATE TABLE competences (
    id BIGSERIAL PRIMARY KEY,
    job_posting_id BIGINT NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    original_term VARCHAR(255) NOT NULL,        -- Original-Text aus Dokument
    esco_label VARCHAR(255),                    -- ESCO-Skill-Name
    esco_uri VARCHAR(500),                      -- https://data.europa.eu/esco/skill/...
    confidence_score DOUBLE PRECISION,          -- 0.0-1.0
    esco_group_code VARCHAR(50),                -- Ebene 3 (Skill-Kategorie)
    is_digital BOOLEAN DEFAULT false,           -- Ebene 3
    is_discovery BOOLEAN DEFAULT false,         -- Ebene 1 (Neu entdeckt?)
    level INTEGER,                              -- 2, 4 oder 5 (ESCO-Niveau)
    role_context VARCHAR(255),                  -- Ebene 6 (Jobbezeichnung)
    source_domain VARCHAR(100),                 -- Ebene 4/5 ("Softgarden", etc.)
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indices
CREATE INDEX idx_competences_job_posting_id ON competences(job_posting_id);
CREATE INDEX idx_competences_esco_uri ON competences(esco_uri);
CREATE INDEX idx_competences_is_discovery ON competences(is_discovery);
CREATE INDEX idx_competences_original_term ON competences(original_term);
CREATE INDEX idx_competences_confidence_score ON competences(confidence_score);
```

**Ebenen (7-Schichten-Modell):**
- **Ebene 1:** `is_discovery` - Ist neu entdeckt?
- **Ebene 2:** `level` - ESCO-Niveau (2, 4, 5)
- **Ebene 3:** `esco_group_code`, `is_digital` - Skill-Kategorie & Digital
- **Ebene 4/5:** `source_domain` - Wo entdeckt? (Portal)
- **Ebene 6:** `role_context` - Jobbezeichnung
- **Ebene 7:** `job_posting_id` - Idempotenz-Check via raw_text_hash

---

### 3. esco_skills
**ESCO-Datensätze (Referenztabelle)**

```sql
CREATE TABLE esco_skills (
    id BIGSERIAL PRIMARY KEY,
    esco_uri VARCHAR(500) UNIQUE NOT NULL,      -- https://data.europa.eu/esco/skill/...
    preferred_label VARCHAR(255) NOT NULL,      -- Skill-Name
    description TEXT,                           -- Beschreibung
    skill_type VARCHAR(50),                     -- "knowledge" oder "competence"
    reuse_level VARCHAR(50),
    related_occupations TEXT,                   -- JSON: [occupation1, occupation2]
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indices
CREATE INDEX idx_esco_skills_esco_uri ON esco_skills(esco_uri);
CREATE INDEX idx_esco_skills_preferred_label ON esco_skills(preferred_label);
```

**Herkunft:** Von Python-Backend aus ESCO-Files geladen (~17000 Skills)

---

### 4. discovery_candidates
**Neue/ungekannte Skills**

```sql
CREATE TABLE discovery_candidates (
    id BIGSERIAL PRIMARY KEY,
    skill_term VARCHAR(255) UNIQUE NOT NULL,    -- Z.B. "Cloud Architecture"
    count INTEGER DEFAULT 1,                    -- Häufigkeit
    first_seen TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW()
);

-- Indices
CREATE INDEX idx_discovery_candidates_skill_term ON discovery_candidates(skill_term);
CREATE INDEX idx_discovery_candidates_count ON discovery_candidates(count DESC);
```

**Workflow:**
1. Python extrahiert Skill, findet keine ESCO-Match
2. Setzt `is_discovery=true` in `competences`
3. Fügt zu `discovery_candidates` hinzu
4. User approves über Streamlit Dashboard
5. Wechsel zu `discovery_approved`

---

### 5. discovery_approved
**Von User genehmigte Skills**

```sql
CREATE TABLE discovery_approved (
    skill_id BIGINT PRIMARY KEY REFERENCES discovery_candidates(id),
    esco_uri VARCHAR(500),                      -- Verlinkte ESCO-URI
    approved_at TIMESTAMP DEFAULT NOW(),
    approved_by VARCHAR(100)                    -- User/Admin
);

-- Indices
CREATE INDEX idx_discovery_approved_esco_uri ON discovery_approved(esco_uri);
```

**Verwendung:** Künftig werden diese Skills automatisch erkannt

---

### 6. skill_blacklist
**Ignorierte Skills**

```sql
CREATE TABLE skill_blacklist (
    id BIGSERIAL PRIMARY KEY,
    skill_term VARCHAR(255) UNIQUE NOT NULL,
    blacklisted_at TIMESTAMP DEFAULT NOW()
);

-- Indices
CREATE INDEX idx_skill_blacklist_skill_term ON skill_blacklist(skill_term);
```

**Verwendung:** Skills die User als falsch markiert hat, werden ignoriert

---

### 7. domain_rules
**Custom Parsing-Regeln**

```sql
CREATE TABLE domain_rules (
    id BIGSERIAL PRIMARY KEY,
    pattern VARCHAR(500) NOT NULL,              -- Regex oder Text-Pattern
    replacement VARCHAR(500),                   -- Ersatz
    domain VARCHAR(100),                        -- Z.B. "softgarden.de"
    description VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- Indices
CREATE INDEX idx_domain_rules_domain ON domain_rules(domain);
CREATE INDEX idx_domain_rules_is_active ON domain_rules(is_active);
```

**Beispiel:**
```
pattern: "Java(Script)?"
replacement: "JavaScript"
domain: "softgarden.de"
```

---

### 8. audit_log
**Änderungshistorie**

```sql
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    entity_type VARCHAR(100),                   -- "job_posting", "competence", etc.
    entity_id BIGINT,
    action VARCHAR(50),                         -- "INSERT", "UPDATE", "DELETE"
    old_value TEXT,                             -- JSON: alte Werte
    new_value TEXT,                             -- JSON: neue Werte
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT NOW()
);

-- Indices
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at DESC);
```

**Verwendung:** Tracking von Änderungen (wer hat was wann gemacht)

---

## 🔗 Beziehungen (ERD)

```
job_postings (1)
    ↓
    └─ (N) competences
         ├─→ esco_skills (Optional)
         └─→ discovery_candidates (Optional, wenn is_discovery=true)
                └─ (1) discovery_approved

skill_blacklist (Unabhängig, nur Block-List)
domain_rules (Unabhängig, Config)
audit_log (Allgemein, trackt alles)
```

---

## 📊 Häufige Queries

### Alle Skills für einen Job
```sql
SELECT c.*, e.preferred_label
FROM competences c
LEFT JOIN esco_skills e ON c.esco_uri = e.esco_uri
WHERE c.job_posting_id = 123
ORDER BY c.confidence_score DESC;
```

### Neue Skills (Discovery)
```sql
SELECT DISTINCT original_term, COUNT(*) as count
FROM competences
WHERE is_discovery = true
GROUP BY original_term
ORDER BY count DESC;
```

### Top Skills
```sql
SELECT esco_label, COUNT(*) as count
FROM competences
WHERE esco_label IS NOT NULL
GROUP BY esco_label
ORDER BY count DESC
LIMIT 20;
```

### Jobs der letzten Woche
```sql
SELECT * FROM job_postings
WHERE created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
```

### Skills pro Org
```sql
SELECT jp.organization, COUNT(DISTINCT c.id) as skill_count
FROM job_postings jp
JOIN competences c ON jp.id = c.job_posting_id
GROUP BY jp.organization
ORDER BY skill_count DESC;
```

---

## 🔒 Constraints & Validierung

```sql
-- Nicht-Null Constraints
ALTER TABLE competences
ADD CONSTRAINT check_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1);

-- Unique Constraints
ALTER TABLE job_postings
ADD CONSTRAINT unique_raw_text_hash UNIQUE (raw_text_hash);

-- Foreign Key Constraints (automatisch über REFERENCES)
-- job_postings → competences (CASCADE DELETE)
-- esco_skills → competences (ON UPDATE CASCADE)

-- Check Constraints für Level
ALTER TABLE competences
ADD CONSTRAINT check_level CHECK (level IN (2, 4, 5, NULL));
```

---

## 📈 Performance-Tipps

1. **Indices:** Auf häufig gefilterte Spalten
   - `job_posting_id`, `esco_uri`, `is_discovery`
   - `created_at`, `organization`, `job_role`

2. **Pagination:** Bei großen Ergebnismengen
   ```sql
   SELECT * FROM job_postings
   ORDER BY created_at DESC
   LIMIT 20 OFFSET 40;  -- Seite 3 (20 Items)
   ```

3. **Connection Pooling:** Kotlin/Python sollte DB-Connection-Pool nutzen

4. **Vacuum:** Regelmäßige Maintenance
   ```sql
   VACUUM ANALYZE;  -- Cleanup & Statistiken
   ```

---

[← Zurück zu Architecture Index](./index.md)
**Letzte Aktualisierung:** 2025-12-28
