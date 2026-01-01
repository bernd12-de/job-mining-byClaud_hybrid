"""
DiscoveryLearningService - Selbstlernendes System für ESCO-Integration
========================================================================

Automatisches Lernen und Eingliedern neuer Entities:
- Neue Rollen (Ebene 1) → ESCO-Klassifizierung (Ebene 2-5)
- Neue Fähigkeiten (Discovery) → Kompetenz-Taxonomie
- Neue Industrien (unbekannt) → Branchen-Klassifizierung

Prinzip:
1. **Discovery (Ebene 1):** Neue unbekannte Entity entdeckt
2. **Analyse:** Pattern-Matching, Similarity, Kontext-Analyse
3. **Klassifizierung:** Zuordnung zu ESCO/Fachbuch/Academia (Ebene 2-5)
4. **Learning:** Speicherung für zukünftige Verwendung
5. **Auto-Promotion:** Häufige/validierte Discoveries → höhere Ebenen

7-Ebenen-Modell Integration:
- Ebene 1: Discovery (neu entdeckt)
- Ebene 2: ESCO Standard (validiert, ins System übernommen)
- Ebene 3: ESCO Digital (als digital klassifiziert)
- Ebene 4: Fachbuch (in Fachliteratur bestätigt)
- Ebene 5: Academia (in wissenschaftlichen Quellen)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
from collections import defaultdict


class DiscoveryLearningService:
    """
    Selbstlernendes System für automatische ESCO-Integration.

    Workflow:
    1. Neue Entity entdecken (Level 1)
    2. Analysieren & klassifizieren
    3. In Wissensbasis eingliedern
    4. Bei Validierung: Level erhöhen
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).resolve().parents[3] / "data" / "discovery"

        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Discovery Storage
        self.discovered_roles_file = self.data_dir / "discovered_roles.json"
        self.discovered_skills_file = self.data_dir / "discovered_skills.json"
        self.discovered_industries_file = self.data_dir / "discovered_industries.json"

        # Learning Storage
        self.learning_db_file = self.data_dir / "learning_db.json"

        # Load existing discoveries
        self.discovered_roles: Dict = self._load_json(self.discovered_roles_file)
        self.discovered_skills: Dict = self._load_json(self.discovered_skills_file)
        self.discovered_industries: Dict = self._load_json(self.discovered_industries_file)

        # Learning Database (frequency, context, validation)
        self.learning_db: Dict = self._load_json(self.learning_db_file)

        print(f"✅ DiscoveryLearningService initialisiert:")
        print(f"   • Discovered Roles: {len(self.discovered_roles)}")
        print(f"   • Discovered Skills: {len(self.discovered_skills)}")
        print(f"   • Discovered Industries: {len(self.discovered_industries)}")
        print(f"   • Learning DB Entries: {len(self.learning_db)}")

    # ═══════════════════════════════════════════════════════════════════
    # DISCOVERY: Neue Entities entdecken (Ebene 1)
    # ═══════════════════════════════════════════════════════════════════

    def discover_role(
        self,
        role_text: str,
        job_title: str = "",
        context: str = "",
        confidence: float = 1.0
    ) -> Tuple[str, int]:
        """
        Entdeckt eine neue Rolle und klassifiziert sie.

        Returns:
            (role_name, level)
        """
        normalized_role = self._normalize_text(role_text)

        # Check if already known
        if normalized_role in self.discovered_roles:
            entry = self.discovered_roles[normalized_role]
            entry["frequency"] += 1
            entry["last_seen"] = datetime.now().isoformat()
            self._save_json(self.discovered_roles_file, self.discovered_roles)

            # Auto-Promotion bei häufiger Verwendung
            promoted_level = self._auto_promote_role(normalized_role, entry)
            return normalized_role, promoted_level

        # Neue Rolle: Ebene 1 (Discovery)
        self.discovered_roles[normalized_role] = {
            "original_text": role_text,
            "job_title": job_title,
            "context": context[:200],  # Erste 200 Zeichen
            "level": 1,
            "frequency": 1,
            "confidence": confidence,
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "validated": False,
        }

        self._save_json(self.discovered_roles_file, self.discovered_roles)
        print(f"   🆕 Neue Rolle entdeckt: '{normalized_role}' (Level 1)")

        return normalized_role, 1

    def discover_skill(
        self,
        skill_text: str,
        context: str = "",
        confidence: float = 1.0
    ) -> Tuple[str, int]:
        """
        Entdeckt eine neue Fähigkeit und klassifiziert sie.

        Returns:
            (skill_name, level)
        """
        normalized_skill = self._normalize_text(skill_text)

        # Check if already known
        if normalized_skill in self.discovered_skills:
            entry = self.discovered_skills[normalized_skill]
            entry["frequency"] += 1
            entry["last_seen"] = datetime.now().isoformat()
            self._save_json(self.discovered_skills_file, self.discovered_skills)

            # Auto-Promotion
            promoted_level = self._auto_promote_skill(normalized_skill, entry)
            return normalized_skill, promoted_level

        # Neue Fähigkeit: Ebene 1 (Discovery)
        # Aber: Prüfe ob digital
        is_digital = self._is_digital_keyword(skill_text)
        initial_level = 3 if is_digital else 1

        self.discovered_skills[normalized_skill] = {
            "original_text": skill_text,
            "context": context[:200],
            "level": initial_level,
            "is_digital": is_digital,
            "frequency": 1,
            "confidence": confidence,
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "validated": False,
        }

        self._save_json(self.discovered_skills_file, self.discovered_skills)
        print(f"   🆕 Neue Fähigkeit entdeckt: '{normalized_skill}' (Level {initial_level})")

        return normalized_skill, initial_level

    def discover_industry(
        self,
        industry_text: str,
        company_name: str = "",
        context: str = "",
        confidence: float = 1.0
    ) -> Tuple[str, int]:
        """
        Entdeckt eine neue Industrie und klassifiziert sie.

        Returns:
            (industry_name, level)
        """
        normalized_industry = self._normalize_text(industry_text)

        # Check if already known
        if normalized_industry in self.discovered_industries:
            entry = self.discovered_industries[normalized_industry]
            entry["frequency"] += 1
            entry["last_seen"] = datetime.now().isoformat()
            self._save_json(self.discovered_industries_file, self.discovered_industries)

            # Auto-Promotion
            promoted_level = self._auto_promote_industry(normalized_industry, entry)
            return normalized_industry, promoted_level

        # Neue Industrie: Ebene 1 (Discovery)
        self.discovered_industries[normalized_industry] = {
            "original_text": industry_text,
            "company_name": company_name,
            "context": context[:200],
            "level": 1,
            "frequency": 1,
            "confidence": confidence,
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "validated": False,
        }

        self._save_json(self.discovered_industries_file, self.discovered_industries)
        print(f"   🆕 Neue Industrie entdeckt: '{normalized_industry}' (Level 1)")

        return normalized_industry, 1

    # ═══════════════════════════════════════════════════════════════════
    # AUTO-PROMOTION: Ebene 1 → höhere Ebenen
    # ═══════════════════════════════════════════════════════════════════

    def _auto_promote_role(self, role_name: str, entry: Dict) -> int:
        """
        Automatische Beförderung einer Rolle bei Validierung.

        Kriterien:
        - Frequency >= 5: Level 1 → 2 (ESCO Standard)
        - Frequency >= 10: Level 2 → 3 (wenn digital)
        - Validated = True: +1 Level
        """
        current_level = entry["level"]
        frequency = entry["frequency"]
        validated = entry.get("validated", False)

        new_level = current_level

        # Promotion durch Häufigkeit
        if frequency >= 5 and current_level == 1:
            new_level = 2
            print(f"   ⬆️ Auto-Promotion: '{role_name}' L1→L2 (freq={frequency})")

        if frequency >= 10 and current_level == 2:
            # Prüfe ob IT/Digital
            if self._is_digital_role(role_name, entry):
                new_level = 3
                print(f"   ⬆️ Auto-Promotion: '{role_name}' L2→L3 (digital, freq={frequency})")

        # Promotion durch Validierung
        if validated and current_level < 4:
            new_level = min(current_level + 1, 4)
            print(f"   ✅ Validierungs-Promotion: '{role_name}' L{current_level}→L{new_level}")

        # Update
        if new_level != current_level:
            entry["level"] = new_level
            entry["promoted_at"] = datetime.now().isoformat()
            self._save_json(self.discovered_roles_file, self.discovered_roles)

        return new_level

    def _auto_promote_skill(self, skill_name: str, entry: Dict) -> int:
        """Automatische Beförderung einer Fähigkeit."""
        current_level = entry["level"]
        frequency = entry["frequency"]
        validated = entry.get("validated", False)

        new_level = current_level

        # Discovery → ESCO Standard
        if frequency >= 3 and current_level == 1:
            new_level = 2
            print(f"   ⬆️ Auto-Promotion: '{skill_name}' L1→L2 (freq={frequency})")

        # ESCO Standard → Digital
        if frequency >= 8 and current_level == 2 and entry.get("is_digital", False):
            new_level = 3
            print(f"   ⬆️ Auto-Promotion: '{skill_name}' L2→L3 (digital, freq={frequency})")

        # Validierung
        if validated and current_level < 4:
            new_level = min(current_level + 1, 4)
            print(f"   ✅ Validierungs-Promotion: '{skill_name}' L{current_level}→L{new_level}")

        # Update
        if new_level != current_level:
            entry["level"] = new_level
            entry["promoted_at"] = datetime.now().isoformat()
            self._save_json(self.discovered_skills_file, self.discovered_skills)

        return new_level

    def _auto_promote_industry(self, industry_name: str, entry: Dict) -> int:
        """Automatische Beförderung einer Industrie."""
        current_level = entry["level"]
        frequency = entry["frequency"]
        validated = entry.get("validated", False)

        new_level = current_level

        # Discovery → NACE Standard
        if frequency >= 5 and current_level == 1:
            new_level = 2
            print(f"   ⬆️ Auto-Promotion: '{industry_name}' L1→L2 (freq={frequency})")

        # Validierung
        if validated and current_level < 4:
            new_level = min(current_level + 1, 4)
            print(f"   ✅ Validierungs-Promotion: '{industry_name}' L{current_level}→L{new_level}")

        # Update
        if new_level != current_level:
            entry["level"] = new_level
            entry["promoted_at"] = datetime.now().isoformat()
            self._save_json(self.discovered_industries_file, self.discovered_industries)

        return new_level

    # ═══════════════════════════════════════════════════════════════════
    # VALIDATION: Manuelle Bestätigung durch User/Admin
    # ═══════════════════════════════════════════════════════════════════

    def validate_role(self, role_name: str, target_level: Optional[int] = None):
        """Validiert eine Rolle und stuft sie ggf. höher ein."""
        normalized = self._normalize_text(role_name)

        if normalized not in self.discovered_roles:
            print(f"   ⚠️ Rolle '{role_name}' nicht gefunden")
            return

        entry = self.discovered_roles[normalized]
        entry["validated"] = True
        entry["validated_at"] = datetime.now().isoformat()

        if target_level is not None:
            entry["level"] = target_level
            print(f"   ✅ Rolle validiert: '{normalized}' → Level {target_level}")
        else:
            print(f"   ✅ Rolle validiert: '{normalized}'")

        self._save_json(self.discovered_roles_file, self.discovered_roles)

    def validate_skill(self, skill_name: str, target_level: Optional[int] = None):
        """Validiert eine Fähigkeit."""
        normalized = self._normalize_text(skill_name)

        if normalized not in self.discovered_skills:
            print(f"   ⚠️ Fähigkeit '{skill_name}' nicht gefunden")
            return

        entry = self.discovered_skills[normalized]
        entry["validated"] = True
        entry["validated_at"] = datetime.now().isoformat()

        if target_level is not None:
            entry["level"] = target_level
            print(f"   ✅ Fähigkeit validiert: '{normalized}' → Level {target_level}")
        else:
            print(f"   ✅ Fähigkeit validiert: '{normalized}'")

        self._save_json(self.discovered_skills_file, self.discovered_skills)

    def validate_industry(self, industry_name: str, target_level: Optional[int] = None):
        """Validiert eine Industrie."""
        normalized = self._normalize_text(industry_name)

        if normalized not in self.discovered_industries:
            print(f"   ⚠️ Industrie '{industry_name}' nicht gefunden")
            return

        entry = self.discovered_industries[normalized]
        entry["validated"] = True
        entry["validated_at"] = datetime.now().isoformat()

        if target_level is not None:
            entry["level"] = target_level
            print(f"   ✅ Industrie validiert: '{normalized}' → Level {target_level}")
        else:
            print(f"   ✅ Industrie validiert: '{normalized}'")

        self._save_json(self.discovered_industries_file, self.discovered_industries)

    # ═══════════════════════════════════════════════════════════════════
    # EXPORT: Discoveries → ESCO-Format
    # ═══════════════════════════════════════════════════════════════════

    def export_to_esco_format(self, entity_type: str, min_level: int = 2) -> List[Dict]:
        """
        Exportiert validierte Discoveries als ESCO-kompatible Einträge.

        Args:
            entity_type: 'role', 'skill', 'industry'
            min_level: Mindest-Level für Export (default: 2)

        Returns:
            Liste von ESCO-Einträgen
        """
        if entity_type == "role":
            source = self.discovered_roles
        elif entity_type == "skill":
            source = self.discovered_skills
        elif entity_type == "industry":
            source = self.discovered_industries
        else:
            return []

        esco_entries = []

        for name, entry in source.items():
            if entry["level"] >= min_level:
                esco_entry = {
                    "preferredLabel": entry["original_text"],
                    "altLabels": [name],
                    "uri": f"urn:discovery:{entity_type}:{name}",
                    "level": entry["level"],
                    "frequency": entry["frequency"],
                    "validated": entry.get("validated", False),
                    "first_seen": entry["first_seen"],
                }

                if entity_type == "skill":
                    esco_entry["is_digital"] = entry.get("is_digital", False)

                esco_entries.append(esco_entry)

        return esco_entries

    def export_all_to_files(self, output_dir: Optional[Path] = None):
        """Exportiert alle Discoveries als JSON-Dateien."""
        if output_dir is None:
            output_dir = self.data_dir / "exports"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Export Roles
        roles = self.export_to_esco_format("role", min_level=2)
        with (output_dir / "esco_roles.json").open("w", encoding="utf-8") as f:
            json.dump(roles, f, indent=2, ensure_ascii=False)
        print(f"   📄 Exportiert: {len(roles)} Rollen → esco_roles.json")

        # Export Skills
        skills = self.export_to_esco_format("skill", min_level=2)
        with (output_dir / "esco_skills.json").open("w", encoding="utf-8") as f:
            json.dump(skills, f, indent=2, ensure_ascii=False)
        print(f"   📄 Exportiert: {len(skills)} Fähigkeiten → esco_skills.json")

        # Export Industries
        industries = self.export_to_esco_format("industry", min_level=2)
        with (output_dir / "esco_industries.json").open("w", encoding="utf-8") as f:
            json.dump(industries, f, indent=2, ensure_ascii=False)
        print(f"   📄 Exportiert: {len(industries)} Industrien → esco_industries.json")

    # ═══════════════════════════════════════════════════════════════════
    # STATISTICS & REPORTING
    # ═══════════════════════════════════════════════════════════════════

    def get_statistics(self) -> Dict:
        """Gibt Statistiken über Discoveries zurück."""
        roles_by_level = self._group_by_level(self.discovered_roles)
        skills_by_level = self._group_by_level(self.discovered_skills)
        industries_by_level = self._group_by_level(self.discovered_industries)

        return {
            "roles": {
                "total": len(self.discovered_roles),
                "by_level": roles_by_level,
                "validated": sum(1 for e in self.discovered_roles.values() if e.get("validated", False)),
            },
            "skills": {
                "total": len(self.discovered_skills),
                "by_level": skills_by_level,
                "validated": sum(1 for e in self.discovered_skills.values() if e.get("validated", False)),
                "digital": sum(1 for e in self.discovered_skills.values() if e.get("is_digital", False)),
            },
            "industries": {
                "total": len(self.discovered_industries),
                "by_level": industries_by_level,
                "validated": sum(1 for e in self.discovered_industries.values() if e.get("validated", False)),
            },
        }

    def get_top_discoveries(self, entity_type: str, limit: int = 10) -> List[Tuple[str, Dict]]:
        """Gibt die häufigsten Discoveries zurück."""
        if entity_type == "role":
            source = self.discovered_roles
        elif entity_type == "skill":
            source = self.discovered_skills
        elif entity_type == "industry":
            source = self.discovered_industries
        else:
            return []

        sorted_entries = sorted(
            source.items(),
            key=lambda x: x[1]["frequency"],
            reverse=True
        )

        return sorted_entries[:limit]

    # ═══════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════

    def _normalize_text(self, text: str) -> str:
        """Normalisiert Text für Vergleiche."""
        return text.lower().strip()

    def _is_digital_keyword(self, text: str) -> bool:
        """Prüft ob Text Digital-Keywords enthält."""
        digital_keywords = [
            r"\bpython|java|javascript|c\+\+|c#\b",
            r"\bcloud|aws|azure|docker|kubernetes\b",
            r"\bmachine\s+learning|ai|data\s+science\b",
            r"\bsql|database|api|rest\b",
        ]

        text_lower = text.lower()
        for pattern in digital_keywords:
            if re.search(pattern, text_lower):
                return True
        return False

    def _is_digital_role(self, role_name: str, entry: Dict) -> bool:
        """Prüft ob Rolle digital/IT ist."""
        digital_roles = [
            "developer", "engineer", "devops", "data", "software",
            "frontend", "backend", "fullstack", "mobile", "cloud"
        ]

        role_lower = role_name.lower()
        context_lower = entry.get("context", "").lower()

        for keyword in digital_roles:
            if keyword in role_lower or keyword in context_lower:
                return True
        return False

    def _group_by_level(self, source: Dict) -> Dict[int, int]:
        """Gruppiert Einträge nach Level."""
        by_level = defaultdict(int)
        for entry in source.values():
            level = entry.get("level", 1)
            by_level[level] += 1
        return dict(by_level)

    def _load_json(self, file_path: Path) -> Dict:
        """Lädt JSON-Datei."""
        if file_path.exists():
            with file_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_json(self, file_path: Path, data: Dict):
        """Speichert JSON-Datei."""
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    service = DiscoveryLearningService()

    print("\n" + "="*60)
    print("DISCOVERY LEARNING SERVICE - DEMO")
    print("="*60)

    # Simuliere Discoveries
    print("\n📍 Simuliere Discovery-Prozess:\n")

    # Neue Rolle
    service.discover_role("UX Designer", job_title="UX/UI Designer", context="Design Thinking Figma")
    service.discover_role("UX Designer", job_title="Senior UX", context="User Experience")
    service.discover_role("UX Designer", job_title="Lead UX", context="Product Design")

    # Neue Skills
    service.discover_skill("Figma", context="Design Tool UI/UX")
    service.discover_skill("Python", context="Programming Language")
    service.discover_skill("Docker", context="Container Platform")

    # Neue Industrie
    service.discover_industry("Mobility", company_name="Tesla", context="Electric Vehicles")

    # Statistiken
    print("\n📊 Statistiken:")
    stats = service.get_statistics()
    for category, data in stats.items():
        print(f"\n   {category.upper()}:")
        for key, value in data.items():
            print(f"      {key}: {value}")

    # Top Discoveries
    print("\n🏆 Top Discoveries (Roles):")
    top_roles = service.get_top_discoveries("role", limit=5)
    for role_name, entry in top_roles:
        print(f"   • {role_name} (freq={entry['frequency']}, level={entry['level']})")

    print("\n" + "="*60)
    print("✅ Demo abgeschlossen")
    print("="*60)
