# infrastructure/extractor/discovery_extractor.py

from typing import List, Any
import spacy
# WICHTIG: Keine direkten DTO-Imports hier, wir nutzen die Factory des Managers!

class DiscoveryExtractor:
    """
    Ebene 1 (Discovery): Identifiziert Begriffe, die weder in ESCO
    noch in den Fachbuch-Domänen vorhanden sind.
    """

    def __init__(self, repository, manager):
        """
        :param repository: Das HybridCompetenceRepository (SSoT)
        :param manager: Der JobMiningWorkflowManager (Factory)
        """
        self.repository = repository
        self.manager = manager

    def extract_discoveries(self, doc: spacy.tokens.Doc) -> List[Any]:
        """
        Scannt ein SpaCy-Doc nach potenziellen neuen Kompetenzen.
        """
        discoveries = []
        seen_in_doc = set()

        for token in doc:
            # Wissenschaftliche Filterkriterien für Ebene 1:
            # 1. Nur Nomen oder Eigennamen
            # 2. Mindestens 5 Zeichen lang (vermeidet Abkürzungs-Rauschen)
            # 3. Nicht in der Blacklist oder bereits bekannten Domänen

            if token.pos_ in ["NOUN", "PROPN"] and len(token.text) >= 5:
                term_lower = token.text.lower()

                if term_lower in seen_in_doc:
                    continue

                # Blacklist prüfen
                try:
                    if self.repository.is_blacklisted(term_lower):
                        continue
                except Exception:
                    pass

                # Check gegen die gesamte Wissensbasis (Ebene 2, 4, 5)
                if not self.repository.is_known(term_lower):

                    # KERN-FIX: Nutzung der zentralen Factory im Manager
                    # Dies stellt sicher, dass level=1 (int) korrekt gesetzt wird.
                    dto = self.manager.create_competence_dto(
                        original_term=token.text,
                        esco_label="Emergent Skill",
                        esco_uri=f"discovery/{term_lower}",
                        level=1,              # Ebene 1 Marktinnovation
                        is_discovery=True,
                        confidence_score=0.7, # Discovery ist unschärfer als SSoT
                        source_domain="Market Discovery"
                    )

                    if dto:
                        discoveries.append(dto)
                        seen_in_doc.add(term_lower)

        return discoveries

    # Alias für die generische Pipeline (Kompatibel mit CompetenceExtractor)
    def extract(self, doc: spacy.tokens.Doc):
        return self.extract_discoveries(doc)
