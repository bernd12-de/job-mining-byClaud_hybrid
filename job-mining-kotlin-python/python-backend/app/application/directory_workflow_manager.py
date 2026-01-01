"""
Directory Workflow Manager v2.0
================================

✅ BEST PRACTICE: Automatisierter Directory-basierter Workflow

Ergänzt den bestehenden JobMiningWorkflowManager mit
Directory-basiertem Workflow und Archivierung.

Workflow:
1. incoming/     → Neue Dateien
2. processing/   → Verarbeitung
3. archive/      → Archivierung (YYYY-MM)
4. results/      → JSON/CSV
5. reports/      → HTML/Text

Basiert auf: Best_Practice Code Lib/WORKFLOW_DOCUMENTATION.md
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class JobMetadata:
    """Metadata für Job-Anzeige"""
    company: str = ""
    position: str = ""
    date_posted: str = ""
    source: str = ""


class DirectoryWorkflowManager:
    """
    ✅ BEST PRACTICE: Directory-basierter Workflow Manager

    Verzeichnis-Struktur:
    workflow/
    ├── incoming/     📥 Neue Dateien
    ├── processing/   ⚙️ Verarbeitung
    ├── archive/      📁 Archiv (YYYY-MM)
    ├── results/      📊 JSON/CSV
    └── reports/      📝 HTML

    Usage:
        manager = DirectoryWorkflowManager()
        manager.add_job('job.pdf', metadata={...})
        results = manager.run_workflow()
    """

    def __init__(self, base_dir: str = "workflow"):
        self.base_dir = Path(base_dir)
        self._setup_directories()
        logger.info(f"DirectoryWorkflowManager: {self.base_dir}")

    def _setup_directories(self):
        """Erstellt Verzeichnis-Struktur"""
        self.incoming = self.base_dir / "incoming"
        self.processing = self.base_dir / "processing"
        self.archive = self.base_dir / "archive"
        self.results = self.base_dir / "results"
        self.reports = self.base_dir / "reports"

        for d in [self.incoming, self.processing, self.archive, self.results, self.reports]:
            d.mkdir(parents=True, exist_ok=True)

    def add_job(self, file_path: str, metadata: Optional[Dict] = None) -> str:
        """
        Fügt Job zu incoming/ hinzu

        Args:
            file_path: Dateipfad
            metadata: Optional (company, position, etc.)

        Returns:
            Neuer Dateiname
        """
        src = Path(file_path)
        if not src.exists():
            raise FileNotFoundError(f"Not found: {file_path}")

        # Timestamp-Name
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = self.incoming / f"{ts}_{src.name}"

        shutil.copy2(src, dest)
        logger.info(f"📥 Added: {dest.name}")

        # Metadata speichern
        if metadata:
            meta_file = dest.with_suffix(dest.suffix + '.meta.json')
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)

        return dest.name

    def run_workflow(self) -> List[Dict]:
        """
        Führt Workflow aus

        Returns:
            Liste von Ergebnissen
        """
        logger.info("🚀 Workflow START")

        files = [f for f in self.incoming.glob("*") if not f.name.endswith('.meta.json')]

        if not files:
            logger.info("Keine Dateien in incoming/")
            return []

        logger.info(f"Gefunden: {len(files)} Datei(en)")

        results = []
        for f in files:
            try:
                result = self._process(f)
                results.append(result)
            except Exception as e:
                logger.error(f"Fehler bei {f.name}: {e}")

        if results:
            self._export(results)
            self._report(results)

        logger.info(f"✅ Workflow COMPLETE: {len(results)}")
        return results

    def _process(self, file_path: Path) -> Dict:
        """Verarbeitet Datei"""
        logger.info(f"📄 {file_path.name}")

        # Metadata laden
        meta_file = file_path.with_suffix(file_path.suffix + '.meta.json')
        meta = {}
        if meta_file.exists():
            with open(meta_file, 'r') as f:
                meta = json.load(f)

        # Move zu processing
        proc_path = self.processing / file_path.name
        shutil.move(str(file_path), str(proc_path))
        if meta_file.exists():
            shutil.move(str(meta_file), str(self.processing / meta_file.name))

        # Simuliere Analyse
        result = {
            'filename': file_path.name,
            'type': file_path.suffix.lstrip('.'),
            'metadata': meta,
            'processed_at': datetime.now().isoformat()
        }

        # Archiviere
        month = datetime.now().strftime("%Y-%m")
        arch_dir = self.archive / month
        arch_dir.mkdir(exist_ok=True)

        shutil.move(str(proc_path), str(arch_dir / file_path.name))
        if (self.processing / meta_file.name).exists():
            shutil.move(str(self.processing / meta_file.name), str(arch_dir / meta_file.name))

        logger.info(f"✅ Archiviert: {month}/{file_path.name}")
        return result

    def _export(self, results: List[Dict]):
        """Exportiert Ergebnisse"""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON
        json_file = self.results / f"results_{ts}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"📊 JSON: {json_file.name}")

        # CSV
        csv_file = self.results / f"results_{ts}.csv"
        with open(csv_file, 'w') as f:
            f.write("Filename,Type,Company,Position\n")
            for r in results:
                m = r.get('metadata', {})
                f.write(f"{r['filename']},{r['type']},{m.get('company','')},{m.get('position','')}\n")
        logger.info(f"📊 CSV: {csv_file.name}")

    def _report(self, results: List[Dict]):
        """Generiert Reports"""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        # HTML
        html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Job Mining Report</title></head>
<body>
<h1>Job Mining Report</h1>
<p>Generated: {datetime.now()}</p>
<p>Total Jobs: {len(results)}</p>
<table border="1">
<tr><th>Filename</th><th>Type</th><th>Company</th></tr>
"""
        for r in results:
            html += f"<tr><td>{r['filename']}</td><td>{r['type']}</td><td>{r.get('metadata',{}).get('company','N/A')}</td></tr>\n"
        html += "</table></body></html>"

        html_file = self.reports / f"report_{ts}.html"
        with open(html_file, 'w') as f:
            f.write(html)
        logger.info(f"📝 HTML: {html_file.name}")
