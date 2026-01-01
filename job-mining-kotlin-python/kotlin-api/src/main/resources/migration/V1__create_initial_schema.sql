-- Erstellt die Haupttabelle für Stellenausschreibungen
CREATE TABLE IF NOT EXISTS job_posting (
                                           id BIGSERIAL PRIMARY KEY,                          -- BIGSERIAL entspricht Long in Kotlin
                                           title VARCHAR(1024) NOT NULL,
                                           job_role VARCHAR(512) NOT NULL,
                                           raw_text_hash VARCHAR(64) NOT NULL UNIQUE,         -- SHA-256 für Idempotenz (Ebene 7)
                                           raw_text TEXT NOT NULL,
                                           posting_date DATE NOT NULL DEFAULT CURRENT_DATE,   -- DATE für sauberes LocalDate Mapping
                                           region VARCHAR(255) NOT NULL,
                                           industry VARCHAR(512) NOT NULL,
                                           is_segmented BOOLEAN DEFAULT FALSE
);

-- Erstellt die Tabelle für extrahierte Kompetenzen
CREATE TABLE IF NOT EXISTS competence (
                                          id BIGSERIAL PRIMARY KEY,
                                          job_posting_id BIGINT NOT NULL REFERENCES job_posting(id) ON DELETE CASCADE,
                                          original_term VARCHAR(512) NOT NULL,
                                          esco_label VARCHAR(512),
                                          esco_uri VARCHAR(512),
                                          confidence_score DOUBLE PRECISION DEFAULT 0.0,    -- DOUBLE PRECISION für NLP-Scores
                                          esco_group_code VARCHAR(255),
                                          is_digital BOOLEAN DEFAULT FALSE,
                                          is_discovery BOOLEAN DEFAULT FALSE,
                                          level INTEGER DEFAULT 2,                          -- Kompetenzstufe (1-5)
                                          source_domain VARCHAR(255),
                                          role_context VARCHAR(255)
);

-- Index für schnellen Idempotenz-Check
CREATE INDEX IF NOT EXISTS idx_job_posting_hash ON job_posting(raw_text_hash);
