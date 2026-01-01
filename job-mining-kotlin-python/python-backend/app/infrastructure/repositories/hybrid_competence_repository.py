import json
import logging
import os
import re
import requests
from typing import List, Dict, Set, Optional, Any, Pattern

# Imports
from app.interfaces.interfaces import ICompetenceRepository
from app.domain.models import Competence
from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
from app.infrastructure.cache import get_cache_manager

logger = logging.getLogger(__name__)

class HybridCompetenceRepository(ICompetenceRepository):
    # Pfad relativ zum Projekt-Root
    CUSTOM_JSON_PATH = "data/custom_skills_extended.json"

    def __init__(self, rule_client: KotlinRuleClient = None, fachbuch_path: str = None, academia_path: str = None):
        # Backwards-Compatibility: Manche Tests/Clients übergeben 'fachbuch_path' & 'academia_path'
        self._esco_labels: Set[str] = set()
        self._custom_labels: Set[str] = set()
        self._all_competences: List[Competence] = []
        self._esco_mapping: Dict[str, str] = {}
        self._blacklist: Set[str] = set()

        # Falls nur positional args verwendet wurden (legacy), akzeptieren wir das auch
        if isinstance(rule_client, str) and fachbuch_path is None:
            # Ein simpler Fallback: erstes Argument war wahrscheinlich pfad, kein RuleClient
            fachbuch_path = rule_client
            rule_client = None

        self.rule_client = rule_client
        self.fachbuch_path = fachbuch_path
        self.academia_path = academia_path

        # Indexes für schnelle Abfragen
        self.esco_data: Dict[str, Dict] = {}
        self.custom_domains: Dict[str, Dict] = {}
        self._fachbuch_skills: Set[str] = set()
        self._academia_skills: Set[str] = set()
        
        # ✅ BEST PRACTICE: Cache für häufig abgefragte Label-Listen
        self._labels_cache: List[str] = None
        self._identifiable_labels_cache: List[str] = None

        # ✅ PERFORMANCE: Pre-compile regex patterns für digital skills
        self._digital_patterns = self._compile_digital_patterns()

        # Initial laden
        self._load_data()
        # Baue Index für schnellen Lookup
        self._build_esco_index()
        # Lade digitale Skills aus ESCO Collection (optional, mit Fehlerbehandlung)
        try:
            self._load_digital_skills()
        except (AttributeError, Exception) as e:
            logger.warning(f"Digital Skills konnten nicht geladen werden: {e}")
        # Lade lokale Domänen (Ebene 4/5)
        self._load_local_domains_v2()
        # Sync für Legacy Sets (fachbuch / academia)
        self._sync_legacy_sets()
        self._load_custom_skills()
        self._load_dynamic_blacklist()

    def _compile_digital_patterns(self) -> List[Pattern]:
        """Pre-kompiliert Regex-Patterns für digitale Skills (Performance-Optimierung)."""
        digital_keywords = [
            'software', 'digital', 'programm', 'data science', 'daten',
            'cloud', 'machine learning', 'python', 'java', 'javascript',
            'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'typescript',
            'api', 'rest', 'graphql', 'microservices', 'backend', 'frontend',
            'database', 'datenbank', 'nosql', 'mongodb', 'postgresql',
            'web development', 'mobile development', 'app development',
            'coding', 'automation', 'automatisierung', 'agile', 'scrum',
            'devops', 'sap', 'erp', 'crm', 'excel', 'power bi', 'tableau',
            'sql', 'html', 'css', 'react', 'angular', 'vue', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'ki ', 'ai '
        ]

        return [
            re.compile(r'\b' + re.escape(kw.strip()) + r'\b', re.IGNORECASE)
            for kw in digital_keywords
        ]

    def _load_digital_skills(self) -> None:
        """Markiert Skills aus ESCO 'digital' Collection als digital."""
        digital_uri = "http://data.europa.eu/esco/concept-scheme/digital"
        count = 0
        for comp in self._all_competences:
            if hasattr(comp, 'collections') and comp.collections:
                if digital_uri in comp.collections:
                    comp.is_digital = True
                    count += 1
        logger.info(f"✅ {count} digitale Skills aus ESCO Collections markiert.")

    def _load_data(self) -> None:
        """Holt Daten von Kotlin mit Caching. FIX: Tolerant gegen fehlende Keys."""
        cache_manager = get_cache_manager()
        cache_key = "esco_data_from_kotlin"

        # ✅ OPTIMIZATION: Versuche aus Cache zu laden (max 24h alt)
        def fetch_from_kotlin() -> Optional[List[Dict[str, Any]]]:
            """Helper: Lädt Daten frisch von Kotlin"""
            try:
                # URL holen oder Default
                base_url = getattr(self.rule_client, 'base_url', 'http://kotlin-api:8080')

                # SSRF Protection: Validiere URL
                from urllib.parse import urlparse
                parsed = urlparse(base_url)
                allowed_hosts = {'kotlin-api', 'localhost', '127.0.0.1'}

                if parsed.hostname and parsed.hostname not in allowed_hosts:
                    logger.error(f"Sicherheitsfehler: Host nicht erlaubt: {parsed.hostname}")
                    return None

                endpoint = f"{base_url}/api/v1/rules/esco-full"

                logger.info(f"Lade ESCO-Daten von {endpoint}...")
                response = requests.get(endpoint, timeout=15, verify=True, allow_redirects=False)
                logger.debug(f"HTTP-Status: {response.status_code}")

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Kotlin API Fehler: {response.status_code}")
                    return None
            except Exception as e:
                logger.error(f"Fehler beim Laden von Kotlin: {e}")
                return None

        # Lade aus Cache oder frisch von Kotlin
        try:
            data = cache_manager.get_or_compute(
                cache_key=cache_key,
                compute_func=fetch_from_kotlin,
                max_age_hours=24  # Cache 24h gültig
            )
        except Exception as e:
            logger.warning(f"Cache-Fehler: {e}, versuche direkt von Kotlin")
            data = fetch_from_kotlin()

        # Verarbeite Daten
        if data is None or not data:
            logger.warning("Keine Daten von Kotlin/Cache erhalten.")
            # Fallback: Versuche lokale ESCO CSV-Dateien zu laden
            try:
                logger.info("Versuche lokale ESCO CSV-Dateien zu laden...")
                self._load_data_from_local_esco()
            except Exception as le:
                logger.error(f"Lokales Laden fehlgeschlagen: {le}")
            return

        # Debug: Was haben wir geladen?
        logger.debug(f"Response-Type: {type(data)}; Länge: {len(data) if hasattr(data, '__len__') else 'unknown'}")
        first = data[0] if isinstance(data, list) and len(data) > 0 else {}
        logger.debug(f"DEBUG KEYS: {list(first.keys())}")
        logger.debug(f"DEBUG SAMPLE: {first}")

        # Verarbeite Items
        count = 0
        for item in data:
            # FIX: .get() verhindert den Crash ('preferredLabel')
            lbl = (
                item.get('preferredLabel') or
                item.get('preferred_label') or
                item.get('original_term') or
                item.get('esco_label') or
                item.get('term') or
                item.get('label')
            )

            uri = (
                item.get('escoUri') or
                item.get('esco_uri') or
                item.get('uri') or
                item.get('conceptUri') or
                f"unknown/{count}"
            )

            if lbl:
                lbl = lbl.strip()
                self._esco_labels.add(lbl)
                self._all_competences.append(Competence(
                    preferred_label=lbl,
                    esco_uri=uri
                ))
                count += 1

        logger.info(f"✅ {count} Skills erfolgreich geladen (aus Cache oder Kotlin).")

    def _load_custom_skills(self) -> None:
        if os.path.exists(self.CUSTOM_JSON_PATH):
            try:
                with open(self.CUSTOM_JSON_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        # FIX: Auch hier .get() nutzen
                        lbl = item.get('preferredLabel') or item.get('label')
                        if lbl:
                            self._custom_labels.add(lbl)
                            self._all_competences.append(Competence(
                                preferred_label=lbl,
                                esco_uri=item.get('escoUri', 'custom')
                            ))
            except Exception as e:
                logger.warning(f"Custom Skills Fehler: {e}")

    def _load_data_from_local_esco(self) -> None:
        """Lädt ESCO-Daten aus lokalen CSV-Dateien im Ordner `data/esco` als Fallback.
        Erwartet Spalten: preferredLabel, conceptUri oder conceptUri/skillType
        """
        esco_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data', 'esco')
        skills_file = os.path.join(esco_folder, 'skills_de.csv')
        if not os.path.exists(skills_file):
            logger.warning("Lokale ESCO-Datei nicht gefunden: skills_de.csv")
            return

        added = 0
        import csv
        with open(skills_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                lbl = row.get('preferredLabel') or row.get('preferred_label') or row.get('preferredlabel')
                uri = row.get('conceptUri') or row.get('concept_uri') or row.get('concepturi')
                if lbl:
                    self._esco_labels.add(lbl)
                    self._all_competences.append(Competence(preferred_label=lbl, esco_uri=uri or f"local/{added}"))
                    added += 1
        logger.info(f"✅ Lokaler ESCO-Fallback: {added} Begriffe geladen.")

    def _load_dynamic_blacklist(self) -> None:
        try:
            self._blacklist = self.rule_client.fetch_blacklist()
        except (AttributeError, ConnectionError, TimeoutError, Exception) as e:
            logger.warning(f"Blacklist konnte nicht geladen werden: {e}")
            self._blacklist = set()

    # Interface Implementierung
    def get_all_skills(self) -> Set[str]:
        return self._esco_labels.union(self._custom_labels)

    def get_all_competences(self) -> List[Competence]:
        return self._all_competences

    def get_esco_mapping(self) -> Dict[str, str]:
        return self._esco_mapping

    def get_all_identifiable_labels(self) -> List[str]:
        # ✅ BEST PRACTICE: Cache labels to avoid repeated expensive calls
        if self._identifiable_labels_cache is not None:
            return self._identifiable_labels_cache
        
        self._identifiable_labels_cache = list(self.get_all_skills())
        return self._identifiable_labels_cache

    # Backwards-compatibility: older callers expect get_all_labels()
    def get_all_labels(self) -> List[str]:
        # ✅ BEST PRACTICE: Separate cache for backward-compatibility method
        if self._labels_cache is not None:
            return self._labels_cache
        
        self._labels_cache = self.get_all_identifiable_labels()
        return self._labels_cache

    def get_level(self, term: str) -> int:
        """Determine level priority (7-Ebenen-Konzept):
        Level 7 = Zeitreihen/Validierung (nicht implementiert)
        Level 6 = Segmentierung & Kontext (nicht als numerischer Level)
        Level 5 = Academia (modulhandbuch)
        Level 4 = Fachbuch
        Level 3 = ESCO Digital Skills
        Level 2 = ESCO Standard
        Level 1 = Discovery (neue, unbekannte Skills)
        """
        if not term:
            return 2
        t = term.lower().strip()

        # 1) Academia (level 5) - Höchste Priorität für akademische Domänen
        if t in self._academia_skills:
            return 5

        # 2) Fachbuch (level 4) - Domänen-spezifische Skills
        if t in self._fachbuch_skills:
            return 4

        # 3) ESCO lookup mit Digital-Flag
        if t in self.esco_data:
            try:
                meta = self.esco_data[t]
                # Level 3 für digitale ESCO Skills
                if meta.get('is_digital', False):
                    return 3
                # Level 2 für Standard ESCO Skills
                return int(meta.get('level', 2))
            except Exception:
                return 2

        # 4) Custom Domains Check
        for domain_name, domain_data in self.custom_domains.items():
            for comp in domain_data.get('competences', []):
                if comp.get('name', '').lower().strip() == t:
                    return domain_data.get('level', 2)

        # 5) Heuristik: substring match against ESCO labels
        for k, v in self.esco_data.items():
            if t == k or (len(t) > 3 and (t in k or k in t)):
                try:
                    # Digital-Check auch bei Heuristik
                    if v.get('is_digital', False):
                        return 3
                    return int(v.get('level', 2))
                except Exception:
                    return 2

        # Fallback: Level 2 (Standard ESCO)
        return 2

    def get_data_by_label(self, label: str) -> Dict:
        """Returns metadata dict for a given label if found in the repository."""
        if not label:
            return None

        label_l = label.lower().strip()
        # 1) direct index
        if label_l in self.esco_data:
            return self.esco_data[label_l]

        # 2) search _all_competences as fallback
        for comp in self._all_competences:
            try:
                if getattr(comp, 'preferred_label', '').lower() == label_l:
                    return {
                        'uri': getattr(comp, 'esco_uri', None),
                        'preferredLabel': getattr(comp, 'preferred_label', label),
                        'level': getattr(comp, 'level', 3),
                        'is_digital': getattr(comp, 'is_digital', False),
                        'source_domain': getattr(comp, 'source_domain', 'ESCO')
                    }
            except Exception:
                continue
        return None

    def _build_esco_index(self):
        """Builds `self.esco_data` dict from `self._all_competences` for fast lookups."""
        self.esco_data = {}
        for comp in self._all_competences:
            try:
                lbl = getattr(comp, 'preferred_label', None)
                if not lbl:
                    continue
                key = lbl.lower()
                self.esco_data[key] = {
                    'uri': getattr(comp, 'esco_uri', None),
                    'preferredLabel': lbl,
                    'level': getattr(comp, 'level', 2),
                    'is_digital': getattr(comp, 'is_digital', False),
                    'source_domain': getattr(comp, 'source_domain', 'ESCO')
                }
            except Exception:
                continue

    def _load_local_domains_v2(self):
        """Loads JSON domains from `data/job_domains` and populates `self.custom_domains`.

        Tries multiple candidate base paths: current working directory first (useful for tests),
        then the repository-relative path (production / container use).
        
        Erkennt automatisch Level basierend auf Pfad:
        - fachbuecher/ oder fachbuch/ → Level 4
        - modulhandbuecher/ oder academia/ → Level 5
        - Ansonsten aus JSON-Metadaten
        """
        self.custom_domains = {}
        candidate_paths = [
            os.path.join(os.getcwd(), 'data', 'job_domains'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data', 'job_domains'),
            # Zusätzliche Pfade für Fachbücher/Academia
            os.path.join(os.getcwd(), 'data', 'fachbuecher'),
            os.path.join(os.getcwd(), 'data', 'modulhandbuecher')
        ]

        base = None
        for p in candidate_paths:
            if os.path.exists(p):
                base = p
                break

        if not base:
            logger.info(f"Keine lokalen Domain-Dateien gefunden in: {candidate_paths}")
            return

        loaded_count = 0
        level_counts = {4: 0, 5: 0, 'other': 0}
        
        for fname in os.listdir(base):
            if not fname.endswith('.json'):
                continue
            path = os.path.join(base, fname)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                domain_name = data.get('domain', os.path.splitext(fname)[0])
                comp_count = len(data.get('competences', []))
                
                # Auto-detect Level basierend auf Pfad oder Dateiname
                if 'level' not in data:
                    if 'fachbuch' in base.lower() or 'fachbuch' in fname.lower():
                        data['level'] = 4
                        logger.debug(f"📚 {fname}: Level 4 (auto) | {comp_count} Skills")
                    elif 'modulhandbuch' in base.lower() or 'academia' in base.lower() or 'modulhandbuch' in fname.lower():
                        data['level'] = 5
                        logger.debug(f"🎓 {fname}: Level 5 (auto) | {comp_count} Skills")
                    else:
                        data['level'] = 2  # Default für unspezifische Domains
                        logger.debug(f"📁 {fname}: Level 2 (default) | {comp_count} Skills")
                else:
                    level = data['level']
                    emoji = "📚" if level == 4 else "🎓" if level == 5 else "📁"
                    logger.debug(f"{emoji} {fname}: Level {level} | {comp_count} Skills")
                
                self.custom_domains[domain_name] = data
                loaded_count += 1
                
                # Zähle nach Level
                lvl = data.get('level', 2)
                if lvl == 4:
                    level_counts[4] += 1
                elif lvl == 5:
                    level_counts[5] += 1
                else:
                    level_counts['other'] += 1
                    
            except Exception as e:
                logger.warning(f"Fehler beim Laden der Domain {fname}: {e}")

        if loaded_count > 0:
            logger.info(f"✅ {loaded_count} Custom Domains geladen: {level_counts[4]} x Level 4, {level_counts[5]} x Level 5, {level_counts['other']} x Andere")

    def _sync_legacy_sets(self):
        """Populate legacy sets for backward-compatible lookup (fachbuch / academia).
        
        Extrahiert Skills aus custom_domains basierend auf Level:
        - Level 4 → _fachbuch_skills
        - Level 5 → _academia_skills
        """
        self._fachbuch_skills = set()
        self._academia_skills = set()
        
        domain_breakdown = []
        
        for domain_name, data in self.custom_domains.items():
            lvl = data.get('level', 2)
            competences = data.get('competences', [])
            
            domain_skills = 0
            for comp in competences:
                # Unterstütze verschiedene Formate
                name = comp.get('name') or comp.get('preferredLabel') or comp.get('label')
                if not name:
                    continue
                    
                name_low = name.lower().strip()
                
                if lvl == 4:
                    self._fachbuch_skills.add(name_low)
                    domain_skills += 1
                elif lvl == 5:
                    self._academia_skills.add(name_low)
                    domain_skills += 1
            
            if lvl in [4, 5] and domain_skills > 0:
                domain_breakdown.append(f"    {domain_name[:40]}: {domain_skills} Skills")
        
        if self._fachbuch_skills or self._academia_skills:
            logger.info("✅ Legacy Sets synchronisiert:")
            logger.info(f"   📚 Fachbuch (L4): {len(self._fachbuch_skills)} unique Skills")
            logger.info(f"   🎓 Academia (L5): {len(self._academia_skills)} unique Skills")
            if domain_breakdown:
                logger.info("\n   Breakdown pro Domain:")
                for line in domain_breakdown:
                    logger.info(line)

    def is_known(self, term: str) -> bool:
        """Check if a given term is known in ESCO or custom skills.

        PERFORMANCE FIX: Only exact matches or significant substrings (>= 4 chars and > 50% of label)
        to avoid false positives like 'er' matching 'Engineer'.
        """
        if not term:
            return False

        term_norm = term.lower().strip()

        # Minimum length check to avoid noise
        if len(term_norm) < 3:
            return False

        # 1. Direct ESCO index (O(1) lookup)
        if term_norm in self.esco_data:
            return True

        # 2. Custom domains names
        if term_norm in {n.lower() for n in self.custom_domains.keys()}:
            return True

        # 3. Exact match in labels (fast path)
        all_skills_lower = {s.lower() for s in self.get_all_skills()}
        if term_norm in all_skills_lower:
            return True

        # 4. RESTRICTED substring match: Only if term is significant
        # (at least 4 chars AND at least 50% of the label length)
        if len(term_norm) >= 4:
            for lbl in self.get_all_skills():
                lbl_norm = lbl.lower()
                if term_norm in lbl_norm and len(term_norm) >= len(lbl_norm) * 0.5:
                    return True

        return False

    def is_blacklisted(self, term: str) -> bool:
        if not term:
            return False
        return term.lower().strip() in {t.lower() for t in self._blacklist}

    def is_digital_skill(self, term: str) -> bool:
        """Prüft, ob ein Skill als digital klassifiziert ist.
        
        Reihenfolge:
        1) ESCO Digital Collection Flag (aus Metadaten)
        2) Keyword-basierte Heuristik (mit Wortgrenzen)
        3) Substring-Match in bekannten digitalen Skills
        """
        if not term:
            return False
        
        t = term.lower().strip()
        
        # 1) Direct ESCO lookup
        if t in self.esco_data:
            if self.esco_data[t].get('is_digital', False):
                return True
        
        # 2) Keyword-basierte Heuristik für digitale Skills (mit pre-compiled patterns)
        # PERFORMANCE: Patterns wurden in __init__ vorkompiliert
        for pattern in self._digital_patterns:
            if pattern.search(t):
                return True
        
        # 3) Substring-Match in bekannten digitalen ESCO Skills
        for k, v in self.esco_data.items():
            if v.get('is_digital', False) and len(t) > 3:
                if t in k or k in t:
                    return True
        
        return False
