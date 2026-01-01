import json
import os
from pathlib import Path
from typing import List

from app.domain.models import AnalysisResultDTO

EXPORT_DIR = Path(os.getenv('BATCH_RESULTS_DIR', 'data/exports/batch_results'))


def ensure_dir() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _filename_for(result: AnalysisResultDTO) -> str:
    # Verwende Hash für Eindeutigkeit, plus safe Titel-Slug
    title = (result.title or 'job').strip().lower()
    safe = ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in title)
    return f"{safe[:60]}_{result.raw_text_hash[:16]}.json"


def save_result(result: AnalysisResultDTO) -> Path:
    ensure_dir()
    out_path = EXPORT_DIR / _filename_for(result)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)
    return out_path


def rebuild_summary() -> Path:
    ensure_dir()
    jobs = list(EXPORT_DIR.glob('*.json'))
    processed = 0
    skills_total = 0
    for p in jobs:
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            processed += 1
            skills_total += len(data.get('competences', []))
        except Exception:
            continue
    summary = {
        'processed': processed,
        'skills_total': skills_total,
    }
    out = EXPORT_DIR / 'summary.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return out
