import spacy
from typing import List, Optional
from app.interfaces.interfaces import ICompetenceExtractor
from app.domain.models import CompetenceDTO

class CompetenceExtractor(ICompetenceExtractor):
    def __init__(self, spacy_ext, fuzzy_ext, discovery_ext, nlp_model=None):
        self.spacy_ext = spacy_ext
        self.fuzzy_ext = fuzzy_ext
        self.discovery_ext = discovery_ext
        self.nlp = nlp_model or spacy.load("de_core_news_md")

    def extract_competences(self, text: str, role: str) -> List[CompetenceDTO]:
        """Backward-compatible wrapper: akzeptiert (text, role)"""
        return self.extract(text, role)

    def extract(self, text_or_doc, role: str = '') -> List[CompetenceDTO]:
        """Kompatible, bequeme Extraktionsmethode.

        - Akzeptiert entweder einen spaCy `Doc` oder einen `str` Text.
        - Führt die drei Pässe (Spacy, Fuzzy, Discovery) aus und normalisiert die Ergebnisse.
        """
        # Normalisiere auf ein spaCy Doc
        if isinstance(text_or_doc, str):
            doc = self.nlp(text_or_doc)
        else:
            doc = text_or_doc

        # Extraktion
        results = self.spacy_ext.extract(doc)                     # Pass 1: Matcher (Ebene 2/4/5)
        results += self.fuzzy_ext.extract_competences(doc.text)   # Pass 2: Fuzzy (Varianten)
        results += self.discovery_ext.extract(doc)               # Pass 3: Discovery (Ebene 1)

        # Bereinigung und Typ-Sicherung
        return self._merge_and_level_check(results, role)

    def _merge_and_level_check(self, dtos: List[CompetenceDTO], role: str) -> List[CompetenceDTO]:
        seen_uris = set()
        merged = []

        for dto in dtos:
            # 1. Deduplizierung nach URI
            if dto.esco_uri in seen_uris:
                continue

            # 2. Kontext-Zuweisung
            dto.role_context = role

            # 3. TYP-FIX: Erzwinge Integer für 'level' (Kritisch für Kotlin/Jackson)
            if isinstance(dto.level, str):
                # Extrahiere nur Ziffern (z.B. "Ebene 4" -> 4)
                digits = ''.join(filter(str.isdigit, dto.level))
                dto.level = int(digits) if digits else 2

            # Standard-Fallback für Integrität
            if not dto.level:
                dto.level = 2

            merged.append(dto)
            seen_uris.add(dto.esco_uri)

        return merged
