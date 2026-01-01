-- Fügt source_url Spalte für Web-Scraping URLs hinzu
-- Feld ist optional (NULL) für alte Datensätze (File-Uploads)
ALTER TABLE job_posting
ADD COLUMN source_url VARCHAR(2048);

-- Index für schnelle URL-Suche
CREATE INDEX IF NOT EXISTS idx_job_posting_source_url ON job_posting(source_url);
