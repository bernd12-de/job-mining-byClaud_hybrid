-- Erstellt die Tabelle für Blacklist, Industry- und Role-Mappings
CREATE TABLE IF NOT EXISTS domain_rule (
                                           id BIGSERIAL PRIMARY KEY,
                                           rule_type VARCHAR(50) NOT NULL,                   -- 'BLACKLIST', 'INDUSTRY_MAPPING', etc.
    rule_key VARCHAR(512) NOT NULL,
    rule_value TEXT,                                  -- Kann für Blacklist NULL sein
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    -- WICHTIG: Erlaubt denselben Key für unterschiedliche Regeltypen
    CONSTRAINT unique_rule_type_key UNIQUE (rule_type, rule_key)
    );

-- Initiales Befüllen der Blacklist
INSERT INTO domain_rule (rule_type, rule_key) VALUES
                                                  ('BLACKLIST', 'kenntnisse'), ('BLACKLIST', 'fähigkeiten'), ('BLACKLIST', 'kommunikation'),
                                                  ('BLACKLIST', 'deutsch'), ('BLACKLIST', 'englisch'), ('BLACKLIST', 'erfahrung'),
                                                  ('BLACKLIST', 'team'), ('BLACKLIST', 'technik'), ('BLACKLIST', 'bereich'),
                                                  ('BLACKLIST', 'informatik'), ('BLACKLIST', 'digitalisierung'), ('BLACKLIST', 'projektleitung')
    ON CONFLICT (rule_type, rule_key) DO NOTHING;
