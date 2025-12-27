from __future__ import annotations
import csv, re
from pathlib import Path
from typing import Dict, List, Optional

class CompetenceLibrary:
    """Only data + lookup; no text logic."""
    def __init__(self, primary_csv: Optional[Path] = None, extra_csvs: Optional[List[Path]] = None):
        self.competences: Dict[str, Dict] = {}
        if primary_csv:
            self._load_from_csv(primary_csv)
        if extra_csvs:
            for p in extra_csvs or []:
                self._load_from_csv(Path(p))
        if not self.competences:
            self._seed_minimal()
        self._rebuild_lower_index()

    def _load_from_csv(self, path: Path):
        if not path or not Path(path).exists():
            return
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("preferredLabel") or row.get("name") or row.get("Name") or "").strip()
                if not name: continue
                category = (row.get("skillType") or row.get("category") or row.get("Category") or "General").strip()
                ctype = (row.get("type") or row.get("Type") or "skill").strip().lower()
                uri   = (row.get("conceptUri") or row.get("uri") or f"csv:{name}").strip()
                alts  = [a.strip() for a in re.split(r"[|;,]", (row.get("altLabels") or row.get("alternative_labels") or "")) if a.strip()]
                self._upsert(name, category, ctype, uri, alts)

    def _upsert(self, name, category, ctype, uri, alts):
        ex = self.competences.get(name, {"alternative_labels": []})
        ex["category"] = ex.get("category") or category
        ex["type"]     = ex.get("type") or ctype
        ex["uri"]      = ex.get("uri") or uri
        ex["alternative_labels"] = sorted(list(set((ex.get("alternative_labels") or []) + alts)))
        self.competences[name] = ex

    def _seed_minimal(self):
        base = [
            ("Figma","UX Tools","tool","esco:figma",["Figma Design"]),
            ("Sketch","UX Tools","tool","esco:sketch",[]),
            ("Wireframing","Design Activity","skill","esco:wireframing",["Wireframes"]),
            ("User Research","Research Method","method","esco:user-research",["UX Research","Nutzerforschung"]),
            ("Usability Testing","Research Method","method","esco:usability-testing",["Usability Test"]),
            ("Scrum","Agile Method","method","esco:scrum",[]),
            ("SAFe","Agile Framework","framework","esco:safe",["Scaled Agile"]),
            ("HTML5","Web Technology","technology","esco:html5",["HTML"]),
            ("CSS3","Web Technology","technology","esco:css3",["CSS"]),
            ("JavaScript","Programming Language","language","esco:javascript",["JS","ECMAScript"]),
        ]
        for n,c,t,uri,alts in base: self._upsert(n,c,t,uri,alts)

    def _rebuild_lower_index(self):
        self._lower = {}
        for name, data in self.competences.items():
            self._lower[name.lower()] = name
            for alt in data.get("alternative_labels", []):
                if alt: self._lower[alt.lower()] = name

    # Public
    def meta(self, canonical_name: str) -> Dict: return self.competences.get(canonical_name, {})
    def lookup_canonical(self, lower_key: str) -> Optional[str]: return self._lower.get(lower_key)
    def keys_for_matching(self) -> List[str]: return sorted(self._lower.keys(), key=len, reverse=True)
