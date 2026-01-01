import spacy
from spacy.matcher import PhraseMatcher
from typing import List, Optional
from spacy.util import is_package
from app.domain.models import CompetenceDTO
# NEU: Importiere die Factory statt den Manager
from app.application.factories.analysis_result_factory import AnalysisResultFactory
from app.interfaces.interfaces import ICompetenceExtractor

class SpaCyCompetenceExtractor(ICompetenceExtractor):

    def __init__(self, repository=None, manager=None, esco_service=None, domain_rule_service=None, nlp_model=None):
        """Kompatibler Konstruktor: Akzeptiert `repository` (neu), oder die alten Parameter
        `manager`, `esco_service` und `domain_rule_service` (Legacy)."""
        MODEL_NAME = "de_core_news_md"

        # Speichere optionale Services für spätere Nutzung
        self.esco_service = esco_service
        self.domain_rule_service = domain_rule_service
        self.manager = manager

        # Legacy-Adapter: Wenn kein Repository gegeben, versuche aus manager oder esco_service
        if repository is None:
            if manager is not None and hasattr(manager, 'get_all_identifiable_labels'):
                repository = manager
            elif esco_service is not None:
                # Erzeuge einen kleinen Adapter, der die benötigten Methoden bereitstellt
                class _EscoAdapter:
                    def __init__(self, esco):
                        self.esco = esco

                    def get_all_identifiable_labels(self):
                        return list(self.esco.get_esco_target_labels() or [])

                    def get_level(self, term: str):
                        return 3

                    def is_digital_skill(self, term: str):
                        return False

                    # Optional: Methoden zum direkten Zugriff, werden in Extraktor genutzt
                    def get_esco_uri_and_id(self, label: str):
                        return getattr(self.esco, 'get_esco_uri_and_id', lambda x: (None, None, None))(label)

                    def get_esco_mapping(self):
                        return getattr(self.esco, 'get_esco_mapping', lambda: {})()

                repository = _EscoAdapter(esco_service)
            else:
                raise ValueError("SpaCyCompetenceExtractor benötigt ein 'repository' oder 'esco_service' bzw. 'manager'.")

        if nlp_model:
            self.nlp = nlp_model
        else:
            if not is_package(MODEL_NAME):
                spacy.cli.download(MODEL_NAME)
            self.nlp = spacy.load(MODEL_NAME)

        # Kompatibilitäts-Alias: 'extract' wird in der Pipeline erwartet
        def _extract_alias(doc_or_text):
            if isinstance(doc_or_text, str):
                return self.extract_competences(doc_or_text)
            else:
                return self.extract_competences(doc_or_text.text)

        self.extract = _extract_alias

        self.repository = repository
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        # Patterns aus dem Repository laden (SSoT)
        labels = self.repository.get_all_identifiable_labels()
        if labels:
            # Nur Labels verwenden, die mindestens 3 Zeichen sind und keine zu generischen Wörter sind
            generic_words = {'und', 'oder', 'der', 'die', 'das', 'den', 'des', 'dem', 'ein', 'eine', 'einen', 
                           'einer', 'einem', 'eines', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                           'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'}
            filtered_labels = [l for l in labels if len(l) >= 3 and l.lower() not in generic_words]

            # Erzeuge Patterns OHNE zu viele Varianten (verhindert Explosionen)
            patterns = [self.nlp.make_doc(l) for l in filtered_labels[:15000]]  # Erhöht von 10k auf 15k für mehr Skills
            self.matcher.add("KNOWLEDGE_BASE", patterns)
            print(f"✅ spaCy Extractor geladen mit {len(patterns)} Begriffen (gefiltert von {len(labels)} Gesamt).")
        else:
            print("⚠️ spaCy Extractor Warnung: Repository ist leer!")

    def extract_competences(self, text: str, role: str = None) -> List[CompetenceDTO]:
        """
        OPTIMIERTE KOMPETENZEN-EXTRAKTION mit Rollen-Kontextualisierung:
        1. Text-Analyse mit spaCy-NLP
        2. Rollenbasierte Gewichtung (falls Rolle vorhanden)
        3. ESCO-Mapping und Deduplizierung
        """
        if not text: return []
        
        # Role-Context für Gewichtung vorbereiten (Ebene 6: roleContext)
        role_context = role or "Unbekannt"

        doc = self.nlp(text[:100000]) # Limit protection
        matches = self.matcher(doc)
        results = []
        seen = set()

        # Blacklist (Domain-Rule-Service) - optional
        blacklist = set()
        if self.domain_rule_service is not None:
            try:
                blacklist = set(self.domain_rule_service.get_active_blacklist_keys() or [])
            except Exception:
                blacklist = set()

        # Kandidaten aus Repository cachen (für exakte Abgleiche)
        candidates = []
        try:
            candidates = self.repository.get_all_identifiable_labels() if hasattr(self.repository, 'get_all_identifiable_labels') else []
        except Exception:
            candidates = []

        # Approved-Mappings aus gemeinsamer Datei laden (Discovery-Review)
        approved_mapping = {}
        try:
            import os, json
            from pathlib import Path
            base = os.environ.get("BASE_DATA_DIR")
            if base:
                p = Path(base) / "discovery" / "approved_skills.json"
            else:
                p = Path(__file__).resolve().parents[4] / "python-backend" / "data" / "discovery" / "approved_skills.json"
            if p.exists():
                approved_mapping = json.loads(p.read_text(encoding="utf-8")) or {}
        except Exception:
            approved_mapping = {}

        for _, start, end in matches:
            term = doc[start:end].text
            term_lower = term.lower().strip()

            # Einfache Filter: zu kurze Tokens oder keine Buchstaben ignorieren
            if len(term_lower) < 3 or not any(c.isalpha() for c in term_lower):
                continue

            # Prüfe auf exakten Kandidaten (oder kompakte Variante ohne Leerzeichen)
            term_compact = term_lower.replace(' ', '')
            exact_match = None
            for cand in candidates:
                cand_lower = cand.lower()
                if cand_lower == term_lower or cand_lower.replace(' ', '') == term_compact:
                    exact_match = cand
                    break

            # Ermittle, ob es ein Custom-Mapping (z.B. 'jira' -> 'Projektmanagement durchführen') gibt
            mapped = None
            if self.esco_service is not None:
                mapping = getattr(self.esco_service, 'get_esco_mapping', lambda: {})() or {}
                # Merge approved mappings (user-reviewed discovery)
                if approved_mapping:
                    try:
                        mapping = {**mapping, **approved_mapping}
                    except Exception:
                        pass
                mapped = mapping.get(term_lower)

            # Debug: Ausgabe der gefundenen Matches (nur beim direkten Testlauf sichtbar)
            # print(f"DEBUG MATCH: term={term!r}, term_lower={term_lower!r}, exact_match={exact_match}, mapped={mapped}")

            # Wenn weder exakter Kandidat noch Mapping gefunden wurde, überspringe (vermeidet falsche Matches)
            if exact_match is None and mapped is None:
                continue

            # Bestimme das kanonische Label (für Deduplizierung): Mapping hat Vorrang
            canonical_label = (mapped if mapped is not None else exact_match)
            canonical_label_lower = canonical_label.lower().strip()

            # Dedupliziere nach kanonischem ESCO-Label
            if canonical_label_lower in seen:
                continue

            # Blacklist prüfen (sowohl gefundener Term als auch das kanonische Label)
            if term_lower in blacklist or canonical_label_lower in blacklist:
                continue

            seen.add(canonical_label_lower)

            # Versuche ESCO Informationen zu holen, falls vorhanden
            esco_label = canonical_label
            esco_uri = f"custom/{canonical_label_lower.replace(' ', '_')}"
            esco_group_code = None

            try:
                # Versuche zuerst mit dem (möglicherweise) gemappten Label die URI zu holen
                label_to_lookup = esco_label

                if hasattr(self.repository, 'get_esco_uri_and_id'):
                    uri, _id, group = self.repository.get_esco_uri_and_id(label_to_lookup)
                    if uri:
                        esco_uri = uri
                    if group:
                        esco_group_code = group
                elif self.esco_service is not None:
                    uri, _id, group = getattr(self.esco_service, 'get_esco_uri_and_id', lambda x: (None, None, None))(label_to_lookup)
                    if uri:
                        esco_uri = uri
                    if group:
                        esco_group_code = group

                # Falls der gemappte Label-Lookup nicht erfolgreich war, versuche die Kandidaten aus dem Repository zu finden
                if esco_uri.startswith('custom/'):
                    # Suche nach Labels, die den gefundenen Term (oder seine kompakte Form) enthalten
                    candidates = self.repository.get_all_identifiable_labels() if hasattr(self.repository, 'get_all_identifiable_labels') else []
                    found = None
                    term_norm = term_lower.replace(' ', '')
                    for cand in candidates:
                        cand_norm = cand.lower().replace(' ', '')
                        if term_lower in cand_norm or term_compact in cand_norm:
                            found = cand
                            break
                    if found:
                        esco_label = found
                        # Hole URI für das gefundene Label
                        try:
                            uri, _id, group = (
                                self.repository.get_esco_uri_and_id(found)
                                if hasattr(self.repository, 'get_esco_uri_and_id')
                                else (None, None, None)
                            )
                            if uri:
                                esco_uri = uri
                            if group:
                                esco_group_code = group
                        except Exception:
                            pass

            except Exception:
                pass

            # Hole ESCO Collections (digital, research, transversal, language)
            collections = []
            try:
                if hasattr(self.repository, 'get_data_by_label'):
                    esco_data = self.repository.get_data_by_label(esco_label)
                    if esco_data and 'collections' in esco_data:
                        collections = esco_data['collections']
            except Exception:
                pass

            dto = AnalysisResultFactory.create_competence(
                original_term=term,
                esco_label=esco_label,
                esco_uri=esco_uri,
                level=self.repository.get_level(term),
                is_digital=self.repository.is_digital_skill(term),
                collections=collections,
                role_context=role_context,  # Nutze vorbereitetete role_context (Ebene 6)
                confidence=1.0
            )

            # Ergänze optionales Group-Attribut (kompatibel zu alten DTOs)
            if esco_group_code is not None:
                setattr(dto, 'esco_group_code', esco_group_code)

            results.append(dto)

        # Fallback: Verwende einfachen Fuzzy/Substrings-Abgleich über n-grams, falls nichts gefunden wurde
        if not results:
            try:
                from rapidfuzz import fuzz

                labels = self.repository.get_all_identifiable_labels()
                # Filtere Tokens: alphabetische oder hyphenierte Tokens, keine Stop-Words
                tokens = [t.text for t in self.nlp(text) if (t.is_alpha or '-' in t.text) and not t.is_stop]
                if not tokens:
                    return results
                max_n = min(4, max((len(l.split()) for l in labels), default=1))

                def ngrams(seq, n):
                    return [seq[i:i+n] for i in range(len(seq)-n+1)]

                # Hole ggf. Custom-Mapping fürs Fallback
                mapping = getattr(self.esco_service, 'get_esco_mapping', lambda: {})() if self.esco_service is not None else {}
                if approved_mapping:
                    try:
                        mapping = {**mapping, **approved_mapping}
                    except Exception:
                        pass

                # 1) Mapping-Pass: suche gezielt nach Mappings in den Tokens (z.B. 'jira', 'nosql')
                for n in range(1, max_n+1):
                    for gram in ngrams(tokens, n):
                        joined = ''.join(gram).lower()
                        gram_joined_space = ' '.join(gram).lower()
                        mapped_label = mapping.get(gram_joined_space) or mapping.get(joined)
                        # Debug
                        # print(f"MAPPING_PASS: gram={gram_joined_space!r}, mapped_label={mapped_label!r}")
                        if mapped_label and mapped_label.lower() not in seen:
                            uri, _id, group = (self.repository.get_esco_uri_and_id(mapped_label) if hasattr(self.repository, 'get_esco_uri_and_id') else (None, None, None))
                            esco_uri_val = uri if uri else f"custom/{mapped_label.lower().replace(' ', '_')}"
                            dto = AnalysisResultFactory.create_competence(
                                original_term=' '.join(gram),
                                esco_label=mapped_label,
                                esco_uri=esco_uri_val,
                                level=self.repository.get_level(mapped_label),
                                is_digital=self.repository.is_digital_skill(mapped_label),
                                role_context=role
                            )
                            results.append(dto)
                            seen.add(mapped_label.lower())

                # 2) Label-Scan: substring / fuzzy matching (nur für Labels, die noch nicht gefunden wurden)
                for label in labels:
                    if label.lower() in seen:
                        continue
                    # Normiertes, alnum-only Label für Vergleiche (z.B. UX-Testing -> uxtesting)
                    norm_label_raw = ''.join(label.split()).lower()
                    norm_label = ''.join(ch for ch in norm_label_raw if ch.isalnum())
                    found = False
                    for n in range(1, max_n+1):
                        for gram in ngrams(tokens, n):
                            joined_raw = ''.join(gram).lower()
                            # Entferne Nicht-Alphanumerische Zeichen für robustere Vergleiche (z.B. UX-Testing -> uxtesting)
                            joined = ''.join(ch for ch in joined_raw if ch.isalnum())

                            # Substring match (hohe Präzision): kurze joined in längeres norm_label
                            if joined and joined in norm_label:
                                # Erzeuge DTO ähnlich wie beim Matcher
                                esco_uri_val = f"custom/{label.lower().replace(' ', '_')}"
                                try:
                                    uri, _id, group = (self.repository.get_esco_uri_and_id(label) if hasattr(self.repository, 'get_esco_uri_and_id') else (None, None, None))
                                    if uri:
                                        esco_uri_val = uri
                                except Exception:
                                    uri, _id, group = (None, None, None)

                                dto = AnalysisResultFactory.create_competence(
                                    original_term=' '.join(gram),
                                    esco_label=label,
                                    esco_uri=esco_uri_val,
                                    level=self.repository.get_level(label),
                                    is_digital=self.repository.is_digital_skill(label),
                                    role_context=role
                                )
                                # Ergänze optional das Gruppen-Attribut falls vorhanden
                                if group is not None:
                                    setattr(dto, 'esco_group_code', group)

                                # Dedupliziere nach ESCO-Label
                                if label.lower() not in seen:
                                    results.append(dto)
                                    seen.add(label.lower())
                                found = True
                                break
                            # Fuzzy-Check (strenger Threshold um False-Positives zu vermeiden)
                            if len(joined) >= 3:
                                score = fuzz.partial_ratio(norm_label, joined)
                                if score >= 90:
                                    dto = AnalysisResultFactory.create_competence(
                                        original_term=' '.join(gram),
                                        esco_label=label,
                                        esco_uri=f"custom/{label.lower().replace(' ', '_')}",
                                        level=self.repository.get_level(label),
                                        is_digital=self.repository.is_digital_skill(label),
                                        role_context=role
                                    )
                                    if label.lower() not in seen:
                                        results.append(dto)
                                        seen.add(label.lower())
                                    found = True
                                    break
                        if found:
                            break
            except Exception:
                pass

        return results
        return results
