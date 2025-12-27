"""
Hybrid Competence Repository
Kombiniert Custom Skills + ESCO Skills zweigleisig
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Set
from domain.models.competence import Competence, CompetenceSource, CompetenceType


class HybridCompetenceRepository:
    """
    Repository: Hybrid (Custom + ESCO)
    
    Features:
    - Lädt Custom Skills aus JSON
    - Lädt ESCO Skills aus JSON
    - Dedupliziert automatisch
    - Transparent kombinierbar
    """
    
    def __init__(self, 
                 custom_path: str = "data/competences/custom_skills.json",
                 esco_path: str = "data/competences/esco_skills.json"):
        self.custom_path = Path(custom_path)
        self.esco_path = Path(esco_path)
        
        self._custom_skills: List[Competence] = []
        self._esco_skills: List[Competence] = []
        self._all_skills: List[Competence] = []
        
        self._load_all()
    
    def _load_all(self) -> None:
        """Lade beide Skill-Quellen"""
        self._load_custom()
        self._load_esco()
        self._merge()
    
    def _load_custom(self) -> None:
        """Lade Custom Skills"""
        if not self.custom_path.exists():
            print(f"⚠️ Custom Skills nicht gefunden: {self.custom_path}")
            return
        
        with open(self.custom_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Unterstütze beide Formate: Liste ODER Dict mit 'competences' key
        items = data if isinstance(data, list) else data.get('competences', [])
        
        for item in items:
            comp = Competence(
                name=item['name'],
                category=item['category'],
                competence_type=CompetenceType(item.get('competence_type', 'skill')),
                source=CompetenceSource.CUSTOM,
                alternative_labels=item.get('alternative_labels', []),
                confidence_score=1.0
            )
            self._custom_skills.append(comp)
        
        print(f"✅ {len(self._custom_skills)} Custom Skills geladen")
    
    def _load_esco(self) -> None:
        """Lade ESCO Skills"""
        if not self.esco_path.exists():
            print(f"⚠️ ESCO Skills nicht gefunden: {self.esco_path}")
            return
        
        with open(self.esco_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Unterstütze beide Formate: Liste ODER Dict mit 'skills' key
        items = data if isinstance(data, list) else data.get('skills', [])
        
        for item in items:
            comp = Competence(
                name=item['preferredLabel'],
                category=item.get('category', 'General'),
                competence_type=CompetenceType(item.get('skillType', 'skill')),
                source=CompetenceSource.ESCO,
                esco_uri=item.get('conceptUri'),
                esco_code=item.get('code'),
                alternative_labels=item.get('altLabels', []),
                confidence_score=1.0
            )
            self._esco_skills.append(comp)
        
        print(f"✅ {len(self._esco_skills)} ESCO Skills geladen")
    
    def _merge(self) -> None:
        """Merge und dedupliziere"""
        # Alle Skills sammeln
        all_skills = self._custom_skills + self._esco_skills
        
        # Deduplizierung nach Name (case-insensitive)
        seen: Set[str] = set()
        unique_skills: List[Competence] = []
        
        for skill in all_skills:
            name_lower = skill.name.lower()
            if name_lower not in seen:
                seen.add(name_lower)
                unique_skills.append(skill)
        
        self._all_skills = unique_skills
        print(f"✅ {len(self._all_skills)} Skills gesamt (dedupliziert)")
    
    def get_all(self) -> List[Competence]:
        """Alle Skills (Custom + ESCO)"""
        return self._all_skills
    
    def get_custom_only(self) -> List[Competence]:
        """Nur Custom Skills"""
        return self._custom_skills
    
    def get_esco_only(self) -> List[Competence]:
        """Nur ESCO Skills"""
        return self._esco_skills
    
    def get_all_count(self) -> int:
        """Anzahl aller Skills"""
        return len(self._all_skills)
    
    def get_by_category(self, category: str) -> List[Competence]:
        """Skills nach Kategorie"""
        return [s for s in self._all_skills if s.category == category]
    
    def find_by_name(self, name: str) -> Optional[Competence]:
        """Finde Skill nach Name (case-insensitive)"""
        name_lower = name.lower()
        for skill in self._all_skills:
            if skill.name.lower() == name_lower:
                return skill
            # Auch in alternative labels suchen
            for alt in skill.alternative_labels:
                if alt.lower() == name_lower:
                    return skill
        return None
    
    def get_statistics(self) -> Dict:
        """Repository-Statistiken"""
        return {
            'total': len(self._all_skills),
            'custom': len(self._custom_skills),
            'esco': len(self._esco_skills),
            'categories': len(set(s.category for s in self._all_skills)),
            'types': {
                t.value: sum(1 for s in self._all_skills if s.competence_type == t)
                for t in CompetenceType
            }
        }
