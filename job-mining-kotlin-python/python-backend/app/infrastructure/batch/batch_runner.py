"""
Batch Runner mit Fehler-Statistiken
Funktioniert lokal, Docker & Cloud (umgebungsunabhängig)

Features:
- Progress-Tracking (3 von 10 files)
- Fehler-Reports (JSON + CSV)
- Run-Statistik (success/failed/skipped)
- Umgebungserkennung (local/docker/cloud)
"""

import os
import json
import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class RunEnvironment(Enum):
    """Erkannte Umgebung"""
    LOCAL = "local"      # Entwickler-Laptop
    DOCKER = "docker"    # Docker Container
    CLOUD = "cloud"      # VServer/Cloud (Railway, AWS, etc.)


class JobStatus(Enum):
    """Status einer einzelnen Job-Verarbeitung"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class JobResult:
    """Ergebnis einer einzelnen Job-Verarbeitung"""
    filename: str
    status: JobStatus
    competences_found: int
    processing_time_ms: int
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class BatchStatistics:
    """Gesamt-Statistik eines Batch-Runs"""
    run_id: str
    started_at: str
    finished_at: str
    environment: str
    total_files: int
    successful: int
    failed: int
    skipped: int
    total_competences: int
    total_time_ms: int
    avg_time_per_file_ms: float
    results: List[Dict[str, Any]]
    errors: List[Dict[str, str]]
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dict für JSON-Export"""
        return asdict(self)
    
    def to_csv_rows(self) -> List[Dict]:
        """Konvertiert zu Zeilen für CSV-Export"""
        rows = []
        for result in self.results:
            rows.append({
                'run_id': self.run_id,
                'filename': result['filename'],
                'status': result['status'],
                'competences': result['competences_found'],
                'time_ms': result['processing_time_ms'],
                'error': result.get('error_message', ''),
                'environment': self.environment,
                'timestamp': self.started_at
            })
        return rows


class BatchRunner:
    """
    Batch-Verarbeitung mit Statistiken
    Funktioniert in allen Umgebungen (local/docker/cloud)
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Args:
            output_dir: Verzeichnis für Reports (None = auto-detect)
        """
        self.environment = self._detect_environment()
        self.output_dir = output_dir or self._get_default_output_dir()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🚀 BatchRunner initialisiert: {self.environment.value} → {self.output_dir}")
    
    def _detect_environment(self) -> RunEnvironment:
        """Erkennt die Laufzeit-Umgebung"""
        # Docker: /.dockerenv existiert
        if os.path.exists('/.dockerenv'):
            return RunEnvironment.DOCKER
        
        # Cloud: Typische ENV-Variablen (Railway, Heroku, AWS, etc.)
        cloud_indicators = [
            'RAILWAY_ENVIRONMENT', 'DYNO', 'AWS_EXECUTION_ENV',
            'KUBERNETES_SERVICE_HOST', 'GOOGLE_CLOUD_PROJECT'
        ]
        if any(os.getenv(var) for var in cloud_indicators):
            return RunEnvironment.CLOUD
        
        # Default: Local
        return RunEnvironment.LOCAL
    
    def _get_default_output_dir(self) -> Path:
        """Bestimmt Standard-Output basierend auf Umgebung"""
        if self.environment == RunEnvironment.LOCAL:
            # Lokal: ins Projekt-Verzeichnis
            return Path.cwd() / "batch_reports"
        elif self.environment == RunEnvironment.DOCKER:
            # Docker: gemountetes Volume oder tmp
            if os.path.exists('/app/data/reports'):
                return Path('/app/data/reports')
            return Path('/tmp/batch_reports')
        else:  # CLOUD
            # Cloud: tmp (sollte persistent storage haben)
            return Path('/tmp/batch_reports')
    
    def run_batch(
        self,
        files: List[Path],
        processor_func,
        skip_existing: bool = True,
        save_reports: bool = True
    ) -> BatchStatistics:
        """
        Hauptmethode: Verarbeitet Batch mit Fortschrittsanzeige
        
        Args:
            files: Liste der zu verarbeitenden Dateien
            processor_func: Callable(file_path) -> JobResult
            skip_existing: Überspringe bereits verarbeitete (via Hash)
            save_reports: Speichere JSON/CSV Reports
        
        Returns:
            BatchStatistics mit allen Ergebnissen
        """
        run_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        started_at = datetime.now().isoformat()
        
        logger.info(f"📂 BATCH START: {len(files)} Dateien | Run-ID: {run_id}")
        
        results: List[JobResult] = []
        total_competences = 0
        start_time_ms = int(time.time() * 1000)
        
        for idx, file_path in enumerate(files, start=1):
            # Progress-Anzeige
            percentage = (idx * 100) // len(files)
            progress_bar = "█" * (percentage // 5) + "░" * (20 - percentage // 5)
            
            logger.info(f"📈 BATCH [{progress_bar}] {idx}/{len(files)} ({percentage}%)")
            
            # Verarbeite Datei
            try:
                result = processor_func(file_path)
                results.append(result)
                
                if result.status == JobStatus.SUCCESS:
                    total_competences += result.competences_found
                    logger.info(f"   ✅ {file_path.name}: {result.competences_found} Kompetenzen")
                elif result.status == JobStatus.FAILED:
                    logger.error(f"   ❌ {file_path.name}: {result.error_message}")
                else:  # SKIPPED
                    logger.info(f"   ⏭️  {file_path.name}: Übersprungen")
            
            except Exception as e:
                # Fallback bei unerwarteten Fehlern
                logger.exception(f"   💥 {file_path.name}: Kritischer Fehler")
                results.append(JobResult(
                    filename=file_path.name,
                    status=JobStatus.FAILED,
                    competences_found=0,
                    processing_time_ms=0,
                    error_message=str(e)
                ))
        
        # Finale Statistik
        finished_at = datetime.now().isoformat()
        total_time_ms = int(time.time() * 1000) - start_time_ms
        
        stats = BatchStatistics(
            run_id=run_id,
            started_at=started_at,
            finished_at=finished_at,
            environment=self.environment.value,
            total_files=len(files),
            successful=sum(1 for r in results if r.status == JobStatus.SUCCESS),
            failed=sum(1 for r in results if r.status == JobStatus.FAILED),
            skipped=sum(1 for r in results if r.status == JobStatus.SKIPPED),
            total_competences=total_competences,
            total_time_ms=total_time_ms,
            avg_time_per_file_ms=total_time_ms / len(files) if files else 0,
            results=[asdict(r) for r in results],
            errors=[
                {'filename': r.filename, 'error': r.error_message}
                for r in results if r.status == JobStatus.FAILED
            ]
        )
        
        # Reports speichern
        if save_reports:
            self._save_reports(stats)
        
        # Log finale Zusammenfassung
        logger.info(f"""
╔══════════════════════════════════════════════════════════════╗
║ 🎯 BATCH ABGESCHLOSSEN                                       ║
╠══════════════════════════════════════════════════════════════╣
║  Run-ID:     {run_id:44} ║
║  Umgebung:   {self.environment.value:44} ║
║  Dateien:    {len(files):44} ║
║  ✅ Erfolg:   {stats.successful:44} ║
║  ❌ Fehler:   {stats.failed:44} ║
║  ⏭️  Skip:     {stats.skipped:44} ║
║  💡 Skills:   {total_competences:44} ║
║  ⏱️  Zeit:     {total_time_ms/1000:.1f}s{' '*(40)}║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        return stats
    
    def _save_reports(self, stats: BatchStatistics):
        """Speichert JSON + CSV Reports"""
        # JSON Report (vollständig)
        json_path = self.output_dir / f"{stats.run_id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(stats.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"💾 JSON Report: {json_path}")
        
        # CSV Report (kompakt für Excel)
        try:
            import csv
            csv_path = self.output_dir / f"{stats.run_id}.csv"
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                if stats.results:
                    fieldnames = stats.to_csv_rows()[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(stats.to_csv_rows())
            logger.info(f"💾 CSV Report: {csv_path}")
        except Exception as e:
            logger.warning(f"CSV Export fehlgeschlagen: {e}")
    
    def get_latest_report(self) -> Optional[BatchStatistics]:
        """Holt den neuesten Report aus dem Output-Verzeichnis"""
        json_files = sorted(self.output_dir.glob("batch_*.json"), reverse=True)
        if not json_files:
            return None
        
        with open(json_files[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return BatchStatistics(**data)
