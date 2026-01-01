import json
import os
from pathlib import Path
from typing import List, Dict


def _data_base_dir() -> Path:
    base = os.environ.get("BASE_DATA_DIR")
    if base:
        return Path(base)
    # Fallback: relative zum repo
    return Path(__file__).resolve().parents[4] / "python-backend" / "data"


def _ensure_discovery_dir(base: Path) -> Path:
    d = base / "discovery"
    d.mkdir(parents=True, exist_ok=True)
    return d


def log_candidates(candidates: List[Dict]):
    """Persistiert Kandidaten in /data/discovery/candidates.json (append + merge)."""
    base = _data_base_dir()
    ddir = _ensure_discovery_dir(base)
    fpath = ddir / "candidates.json"
    ignore_path = ddir / "ignore_skills.json"

    existing: List[Dict] = []
    if fpath.exists():
        try:
            existing = json.loads(fpath.read_text(encoding="utf-8")) or []
        except Exception:
            existing = []

    # Merge nach Schlüssel (term + role)
    index = {}
    for item in existing:
        key = (str(item.get("term", "")).lower().strip(), str(item.get("role", "")).lower().strip())
        index[key] = item

    # Ignorierte Begriffe laden
    ignored = set()
    if ignore_path.exists():
        try:
            ignored_list = json.loads(ignore_path.read_text(encoding="utf-8")) or []
            ignored = {str(x).lower().strip() for x in ignored_list}
        except Exception:
            ignored = set()

    for cand in candidates:
        key = (str(cand.get("term", "")).lower().strip(), str(cand.get("role", "")).lower().strip())
        # Überspringe ignorierte Begriffe
        if key[0] in ignored:
            continue
        if key in index:
            # Zähle Häufigkeit hoch
            prev = index[key]
            prev["count"] = int(prev.get("count", 0)) + int(cand.get("count", 1))
        else:
            # Minimalfelder garantieren
            index[key] = {
                "term": cand.get("term"),
                "role": cand.get("role"),
                "context": cand.get("context", ""),
                "count": int(cand.get("count", 1))
            }

    merged = list(index.values())
    fpath.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
