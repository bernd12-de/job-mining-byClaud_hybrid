# 1. Basis-Image mit Python 3.11
FROM python:3.11-slim

# 2. System-Abhängigkeiten (Postgres, Build-Tools, Curl für Healthchecks)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. Installation der Python-Pakete
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Playwright Browser-Setup (Chromium reicht für Scraper)
# Install Playwright only when explicitly requested (avoid failing builds in constrained envs)
ARG INSTALL_PLAYWRIGHT=false
RUN if [ "$INSTALL_PLAYWRIGHT" = "true" ]; then playwright install chromium --with-deps; else echo "Skipping Playwright install (INSTALL_PLAYWRIGHT=$INSTALL_PLAYWRIGHT)"; fi

# 5. Code kopieren
COPY . .

# 6. Startbefehl für die API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
