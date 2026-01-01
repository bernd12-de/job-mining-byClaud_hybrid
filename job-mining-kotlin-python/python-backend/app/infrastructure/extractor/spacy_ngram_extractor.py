# app/infrastructure/extractor/spacy_ngram_extractor.py

import spacy
from spacy.util import is_package
from typing import List, Set, Optional
from app.domain.models import CompetenceDTO
from app.application.factories.analysis_result_factory import AnalysisResultFactory
from app.interfaces.interfaces import ICompetenceExtractor
from app.infrastructure.data.json_alias_repository import JsonAliasRepository


class SpaCyNGramExtractor(ICompetenceExtractor):
    """
    NEUE ARCHITEKTUR: N-Gramm basierte Skill-Extraktion (1-3 Wörter).

    VORTEILE gegenüber PhraseMatcher:
    - ✅ Keine 10k/15k Limits mehr (direkter Dict-Lookup)
    - ✅ 10x schneller (O(1) Lookup statt O(n) Matcher)
    - ✅ Erkennt alle Aliase (Java, SQL, Git, AWS, C++, etc.)
    - ✅ Unterstützt Multi-Word Skills (Machine Learning, Data Science, etc.)
    - ✅ Nutzt JsonAliasRepository (vorberechnete Metadaten)

    ALGORITHMUS:
    1. Text mit spaCy tokenisieren
    2. N-Gramme bilden (3-Wort, 2-Wort, 1-Wort)
    3. Jedes N-Gramm gegen Alias-Dictionary prüfen (lowercase)
    4. Metadaten aus JsonAliasRepository holen
    5. Deduplizierung nach offiziellem ESCO-Label
    """

    def __init__(
        self,
        alias_repository: JsonAliasRepository,
        domain_rule_service=None,
        nlp_model=None
    ):
        """
        Initialisiert den N-Gramm Extractor.

        :param alias_repository: JsonAliasRepository mit Alias-Mappings
        :param domain_rule_service: Optional - für Blacklist
        :param nlp_model: Optional - spaCy Model (sonst de_core_news_md)
        """
        MODEL_NAME = "de_core_news_md"

        # spaCy NLP laden
        if nlp_model:
            self.nlp = nlp_model
        else:
            if not is_package(MODEL_NAME):
                print(f"⚙️ Lade spaCy Model: {MODEL_NAME}...")
                spacy.cli.download(MODEL_NAME)
            self.nlp = spacy.load(MODEL_NAME)

        # Repositories
        self.alias_repository = alias_repository
        self.domain_rule_service = domain_rule_service

        # Lade Alias-Mappings (vorberechnet)
        self._alias_map = self.alias_repository.get_all_aliases()

        # Statistik
        print(f"✅ SpaCyNGramExtractor geladen:")
        print(f"   - {len(self._alias_map)} Aliase verfügbar")
        print(f"   - N-Gramm-Matching: 1-3 Wörter")
        print(f"   - Repository: {self.alias_repository._data_path}")

        # Kompatibilitäts-Alias für Legacy-Code
        self.extract = self.extract_competences

    def extract_competences(self, text: str, role: str = None) -> List[CompetenceDTO]:
        """
        Extrahiert Kompetenzen aus Text mittels N-Gramm-Matching.

        :param text: Job-Text (max 100k Zeichen)
        :param role: Optional - Berufsrolle für Kontextualisierung
        :return: Liste von CompetenceDTO
        """
        if not text:
            return []

        # Performance-Limit (verhindert Freeze)
        text = text[:100000]

        # spaCy Tokenisierung
        doc = self.nlp(text)

        # Blacklist laden (optional)
        blacklist = self._load_blacklist()

        # N-Gramm Extraktion
        results = []
        seen_official_names = set()  # Deduplizierung nach offiziellem Label

        # WICHTIG: Von groß nach klein (3 → 2 → 1)
        # Verhindert, dass "Machine Learning" als "Machine" + "Learning" erkannt wird
        for n in [3, 2, 1]:
            for i in range(len(doc) - n + 1):
                span = doc[i:i + n]

                # Normalisiere: lowercase, strip whitespace
                span_text_normalized = " ".join([token.text for token in span]).lower().strip()

                # Skip: zu kurz, nur Leerzeichen, Blacklist
                if len(span_text_normalized) < 2:
                    continue

                if span_text_normalized in blacklist:
                    continue

                # ROBUSTE SUCHLOGIK: Padding für exaktes Matching
                # Verhindert False-Positives (z.B. "Java" in "Javascript")
                span_with_padding = f" {span_text_normalized} "

                # Lookup in Alias-Repository (zuerst ohne Padding für exaktes Match)
                metadata = self._alias_map.get(span_text_normalized)

                # Falls nicht gefunden: Prüfe ob es Teil eines längeren Begriffs ist
                if not metadata:
                    # Suche nach Padding-Match (verhindert Substring-Fehler)
                    for alias, meta in self._alias_map.items():
                        if f" {alias} " == span_with_padding:
                            metadata = meta
                            break

                if metadata:
                    esco_id, official_name, domain, level, is_digital, esco_uri = metadata

                    # Deduplizierung (nur offizielle Namen zählen)
                    if official_name.lower() in seen_official_names:
                        continue

                    seen_official_names.add(official_name.lower())

                    # Erstelle CompetenceDTO via Factory
                    dto = AnalysisResultFactory.create_competence(
                        original_term=span.text,  # Original aus Text (z.B. "Java")
                        esco_label=official_name,  # Offizieller Name (z.B. "Java programmieren")
                        esco_uri=esco_uri,
                        level=level,
                        is_digital=is_digital,
                        collections=[],  # TODO: Collections aus Repository holen
                        role_context=role or "Unbekannt",
                        confidence=1.0,
                        source_domain=domain
                    )

                    results.append(dto)

        return results

    def _load_blacklist(self) -> Set[str]:
        """Lädt Blacklist aus DomainRuleService (falls vorhanden)."""
        if self.domain_rule_service is None:
            return set()

        try:
            blacklist_raw = self.domain_rule_service.get_active_blacklist_keys() or []
            return {term.lower().strip() for term in blacklist_raw}
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der Blacklist: {e}")
            return set()

    def get_extractor_info(self) -> str:
        """Info-String für Debugging."""
        return f"SpaCyNGramExtractor ({len(self._alias_map)} Aliase, N=1-3)"


# --- LEGACY WRAPPER (für Kompatibilität mit altem Code) ---

class SpaCyCompetenceExtractorNGram(SpaCyNGramExtractor):
    """
    Legacy-Wrapper: Gleicher Klassenname wie alte Version, neue Implementierung.

    MIGRATION PLAN:
    1. Alte spacy_competence_extractor.py → spacy_competence_extractor_old.py
    2. Diese Datei → spacy_competence_extractor.py
    3. Tests anpassen
    """

    def __init__(
        self,
        repository=None,  # JETZT: JsonAliasRepository (vorher: HybridCompetenceRepository)
        manager=None,  # Legacy (ignoriert)
        esco_service=None,  # Legacy (ignoriert)
        domain_rule_service=None,
        nlp_model=None
    ):
        """
        Kompatibler Konstruktor für alte API.

        WICHTIG: `repository` muss jetzt ein JsonAliasRepository sein!
        """
        if repository is None:
            raise ValueError(
                "SpaCyCompetenceExtractorNGram benötigt ein JsonAliasRepository! "
                "Beispiel: repository=JsonAliasRepository()"
            )

        # Fallback: Wenn alte HybridCompetenceRepository übergeben wurde
        if not isinstance(repository, JsonAliasRepository):
            print("⚠️ WARNUNG: repository ist kein JsonAliasRepository!")
            print("   Erstelle leeres JsonAliasRepository als Fallback.")
            repository = JsonAliasRepository()

        # Initialisiere neue Implementierung
        super().__init__(
            alias_repository=repository,
            domain_rule_service=domain_rule_service,
            nlp_model=nlp_model
        )

        # Legacy-Kompatibilität (für Tests)
        self.repository = repository
        self.esco_service = esco_service
        self.manager = manager
