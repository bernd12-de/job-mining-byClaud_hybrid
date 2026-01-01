#!/bin/bash
# ============================================================================
# Job Mining System - Dependency Installation
# ============================================================================

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  JOB MINING SYSTEM - DEPENDENCY INSTALLATION               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# 1. SYSTEM DEPENDENCIES (APT)
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 SCHRITT 1: System-Pakete installieren"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Benötigte System-Pakete:"
echo "  • tesseract-ocr (OCR Engine)"
echo "  • tesseract-ocr-deu (Deutsches Sprachpaket)"
echo "  • poppler-utils (PDF → Image Converter)"
echo "  • pandoc (DOCX → Markdown Converter)"
echo ""

read -p "System-Pakete installieren? (j/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]; then
    echo "⏳ Installiere System-Pakete..."
    sudo apt-get update
    sudo apt-get install -y \
        tesseract-ocr \
        tesseract-ocr-deu \
        poppler-utils \
        pandoc
    echo "✅ System-Pakete installiert!"
else
    echo "⏭️ System-Pakete übersprungen"
fi

echo ""

# ============================================================================
# 2. PYTHON DEPENDENCIES
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐍 SCHRITT 2: Python Dependencies installieren"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Benötigte Python-Pakete:"
echo "  • Pillow (Image Processing)"
echo "  • pdf2image (PDF → Image)"
echo "  • pytesseract (OCR Wrapper)"
echo "  • sentence-transformers (Semantic Matching, ~500MB)"
echo "  • psycopg2-binary (PostgreSQL)"
echo "  • + alle anderen aus requirements.txt"
echo ""

read -p "Python-Pakete installieren? (j/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]; then
    echo "⏳ Installiere Python-Pakete..."
    cd python-backend
    pip install -r requirements.txt
    echo "✅ Python-Pakete installiert!"
    cd ..
else
    echo "⏭️ Python-Pakete übersprungen"
fi

echo ""

# ============================================================================
# 3. SPACY MODEL
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧠 SCHRITT 3: spaCy Deutsch-Modell installieren"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Benötigtes spaCy-Modell:"
echo "  • de_core_news_md (~50MB)"
echo ""

read -p "spaCy-Modell installieren? (j/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]; then
    echo "⏳ Installiere spaCy-Modell..."
    python -m spacy download de_core_news_md
    echo "✅ spaCy-Modell installiert!"
else
    echo "⏭️ spaCy-Modell übersprungen"
fi

echo ""

# ============================================================================
# 4. VERIFICATION
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SCHRITT 4: Installation überprüfen"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Überprüfe Installationen..."
echo ""

# Tesseract
if command -v tesseract &> /dev/null; then
    version=$(tesseract --version 2>&1 | head -1)
    echo "✅ Tesseract: $version"
else
    echo "❌ Tesseract: NICHT INSTALLIERT"
fi

# Pandoc
if command -v pandoc &> /dev/null; then
    version=$(pandoc --version | head -1)
    echo "✅ Pandoc: $version"
else
    echo "❌ Pandoc: NICHT INSTALLIERT"
fi

# Python Pakete
echo ""
echo "Python-Pakete:"
python -c "import PIL; print(f'✅ Pillow: {PIL.__version__}')" 2>/dev/null || echo "❌ Pillow: NICHT INSTALLIERT"
python -c "import pdf2image; print('✅ pdf2image: Installiert')" 2>/dev/null || echo "❌ pdf2image: NICHT INSTALLIERT"
python -c "import pytesseract; print('✅ pytesseract: Installiert')" 2>/dev/null || echo "❌ pytesseract: NICHT INSTALLIERT"
python -c "import sentence_transformers; print(f'✅ sentence-transformers: {sentence_transformers.__version__}')" 2>/dev/null || echo "❌ sentence-transformers: NICHT INSTALLIERT"
python -c "import psycopg2; print(f'✅ psycopg2: {psycopg2.__version__}')" 2>/dev/null || echo "❌ psycopg2: NICHT INSTALLIERT"
python -c "import spacy; nlp = spacy.load('de_core_news_md'); print(f'✅ spaCy de_core_news_md: Geladen')" 2>/dev/null || echo "❌ spaCy de_core_news_md: NICHT INSTALLIERT"

echo ""

# ============================================================================
# 5. TESTS AUSFÜHREN
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 SCHRITT 5: Tests ausführen (optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
read -p "Alle Tests jetzt ausführen? (j/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]; then
    echo "⏳ Führe Tests aus..."
    echo ""

    cd python-backend

    echo "Test 1: JsonAliasRepository"
    PYTHONPATH=/home/user/job-mining-kotlin-python/python-backend python tests/test_json_alias_repository.py
    echo ""

    echo "Test 2: SpaCyNGramExtractor"
    PYTHONPATH=/home/user/job-mining-kotlin-python/python-backend python tests/test_spacy_ngram_extractor.py
    echo ""

    echo "Test 3: Multi-Format Parser"
    PYTHONPATH=/home/user/job-mining-kotlin-python/python-backend python tests/test_multi_format_parser.py
    echo ""

    echo "Test 4: Directory Workflow"
    PYTHONPATH=/home/user/job-mining-kotlin-python/python-backend python tests/test_directory_workflow.py
    echo ""

    echo "Test 5: ESCO Dual-Mapping"
    PYTHONPATH=/home/user/job-mining-kotlin-python/python-backend python tests/test_esco_dual_mapping.py
    echo ""

    cd ..

    echo "✅ Tests abgeschlossen!"
else
    echo "⏭️ Tests übersprungen"
fi

echo ""

# ============================================================================
# FERTIG
# ============================================================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ INSTALLATION ABGESCHLOSSEN                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Nächste Schritte:"
echo "  1. Starte Python Backend: cd python-backend && python main.py"
echo "  2. Starte Kotlin API: cd kotlin-api && ./gradlew bootRun"
echo "  3. Öffne Dashboard: http://localhost:5000/dashboard/map"
echo ""
echo "Dokumentation:"
echo "  • START_GUIDE.md - Quick Start für alle Deployment-Szenarien"
echo "  • INTEGRATION_GUIDE.md - PostgreSQL Setup"
echo ""
