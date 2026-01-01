#!/usr/bin/env python3
"""
CLI für lokale Batch-Verarbeitung (ohne Docker)
Nutzt den BatchRunner für Statistiken

Usage:
  python cli_batch.py --dir data/jobs
  python cli_batch.py --dir data/jobs --output reports/
  python cli_batch.py --help
"""

import sys
import argparse
import logging
from pathlib import Path

# Stelle sicher, dass app-Modul importierbar ist
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.batch.batch_runner import BatchRunner, JobResult, JobStatus
from app.infrastructure.extractor.advanced_text_extractor import AdvancedTextExtractor
from app.infrastructure.extractor.metadata_extractor import MetadataExtractor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def process_single_file(file_path: Path) -> JobResult:
    """
    Verarbeitet eine einzelne Datei (minimal, ohne DB)
    Simuliert den vollständigen Workflow
    """
    import time
    start_ms = int(time.time() * 1000)
    
    try:
        # 1. Text extrahieren
        text_extractor = AdvancedTextExtractor()
        text = text_extractor.extract_text(str(file_path))
        
        if not text or len(text) < 50:
            return JobResult(
                filename=file_path.name,
                status=JobStatus.FAILED,
                competences_found=0,
                processing_time_ms=int(time.time() * 1000) - start_ms,
                error_message="Zu wenig Text extrahiert"
            )
        
        # 2. Metadaten extrahieren
        metadata_extractor = MetadataExtractor()
        metadata = metadata_extractor.extract_all(text, file_path.name, str(file_path))
        
        # 3. Kompetenzen extrahieren (simuliert)
        # Hier würde normalerweise SpaCy/Fuzzy laufen
        # Für CLI: Zähle einfach Wörter als Proxy
        competences_found = len(text.split()) // 50  # Grobe Schätzung
        
        processing_time_ms = int(time.time() * 1000) - start_ms
        
        return JobResult(
            filename=file_path.name,
            status=JobStatus.SUCCESS,
            competences_found=competences_found,
            processing_time_ms=processing_time_ms,
            warnings=[f"Titel: {metadata.get('job_title', 'N/A')}"]
        )
    
    except Exception as e:
        logger.exception(f"Fehler bei {file_path.name}")
        return JobResult(
            filename=file_path.name,
            status=JobStatus.FAILED,
            competences_found=0,
            processing_time_ms=int(time.time() * 1000) - start_ms,
            error_message=str(e)
        )


def main():
    parser = argparse.ArgumentParser(
        description="Lokale Batch-Verarbeitung mit Fehler-Reports"
    )
    parser.add_argument(
        '--dir',
        type=Path,
        required=True,
        help='Verzeichnis mit Stellenanzeigen (PDF/DOCX/TXT)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=None,
        help='Output-Verzeichnis für Reports (default: auto)'
    )
    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['.pdf', '.docx', '.txt'],
        help='Datei-Endungen (default: .pdf .docx .txt)'
    )
    
    args = parser.parse_args()
    
    # Validierung
    if not args.dir.exists():
        logger.error(f"❌ Verzeichnis nicht gefunden: {args.dir}")
        sys.exit(1)
    
    # Sammle Dateien
    files = []
    for ext in args.extensions:
        files.extend(args.dir.glob(f"**/*{ext}"))
    
    if not files:
        logger.warning(f"⚠️  Keine Dateien gefunden in {args.dir} mit Endungen {args.extensions}")
        sys.exit(0)
    
    logger.info(f"📁 Gefunden: {len(files)} Dateien in {args.dir}")
    
    # Batch-Verarbeitung
    runner = BatchRunner(output_dir=args.output)
    stats = runner.run_batch(
        files=files,
        processor_func=process_single_file,
        save_reports=True
    )
    
    # Zeige Fehler-Details
    if stats.failed > 0:
        logger.error(f"\n🚨 {stats.failed} FEHLER:")
        for error in stats.errors:
            logger.error(f"   ❌ {error['filename']}: {error['error']}")
    
    # Exit-Code
    sys.exit(0 if stats.failed == 0 else 1)


if __name__ == '__main__':
    main()
