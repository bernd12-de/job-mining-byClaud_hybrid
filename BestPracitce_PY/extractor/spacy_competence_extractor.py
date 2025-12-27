# infrastructure/extractor/spacy_competence_extractor.py (MIT HYBRIDEM ESCO-MAPPER)

import spacy
from rapidfuzz import process, fuzz
from typing import List, Optional, Tuple
from core.entities.job_posting import Competence
from core.competence_extraction_interface import CompetenceExtractorInterface
# NEU: Imports der ESCO-Logik
from infrastructure.data.esco_skills import get_esco_mapping, get_esco_target_labels

# --- Lade das deutsche spaCy Modell einmalig ---
try:
    NLP = spacy.load("de_core_news_sm")
except OSError:
    NLP = None

# --- PHASE 2: SEMANTISCHE VORBEREITUNG ---
# WICHTIG: Prüft, ob sentence-transformers im schlanken Deployment verfügbar ist
try:
    from sentence_transformers import SentenceTransformer, util
    SEMANTIC_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    SEMANTIC_MODEL = None

CONFIDENCE_THRESHOLD_P1 = 85  # Lexikalisch
CONFIDENCE_THRESHOLD_P2 = 0.50 # Semantisch
ESCO_EMBEDDINGS = None # Cache für ESCO-Vektoren

# --------------------------------------------------------------------
# A. Hilfsfunktionen (Phase 1 und 2)
# --------------------------------------------------------------------

def _lexical_esco_match(skill: str, esco_labels: List[str]) -> Tuple[Optional[str], float]:
    """ Lexikalisches (Fuzzy) Matching (Phase 1) """
    normalized_skill = skill.lower().strip()
    best_match = process.extractOne(
        query=normalized_skill,
        choices=esco_labels,
        scorer=fuzz.token_set_ratio
    )
    if best_match and best_match[1] >= CONFIDENCE_THRESHOLD_P1:
        return best_match[0], best_match[1]
    return None, 0.0

def _semantic_esco_match(skill: str, esco_labels: List[str]) -> Tuple[Optional[str], float]:
    """ Semantisches Matching (Phase 2) """
    if SEMANTIC_MODEL is None:
        return None, 0.0

    global ESCO_EMBEDDINGS

    # ESCO-Vektoren einmalig cachen
    if ESCO_EMBEDDINGS is None:
        ESCO_EMBEDDINGS = SEMANTIC_MODEL.encode(esco_labels, convert_to_tensor=True)

    # Vektor des Eingabe-Skills berechnen und Kosinus-Ähnlichkeit prüfen
    skill_embedding = SEMANTIC_MODEL.encode([skill], convert_to_tensor=True)
    scores = util.cos_sim(skill_embedding, ESCO_EMBEDDINGS)[0]
    best_score = float(scores.max())

    if best_score >= CONFIDENCE_THRESHOLD_P2:
        best_idx = scores.argmax().item()
        best_match = esco_labels[best_idx]
        return best_match, best_score

    return None, 0.0

# --------------------------------------------------------------------
# B. Haupt-Extractor-Klasse
# --------------------------------------------------------------------

class SpaCyCompetenceExtractor(CompetenceExtractorInterface):

    def __init__(self):
        self.nlp = NLP
        self.esco_map = get_esco_mapping()
        # Löst das dynamische Laden der ESCO-Daten aus!
        self.esco_target_labels = get_esco_target_labels()

    def map_to_esco(self, skill: str) -> str:
        """Führt das Hybride ESCO-Mapping (Phase 1 und 2) aus."""

        # 1. Direkter Match (Fast Lane)
        normalized_skill = skill.lower().strip()
        if normalized_skill in self.esco_map:
            return self.esco_map[normalized_skill]

            # 2. Lexikalisches (Fuzzy) Matching (Phase 1)
        esco_match_p1, score_p1 = _lexical_esco_match(skill, self.esco_target_labels)
        if esco_match_p1:
            return esco_match_p1

        # 3. Semantisches Matching (Phase 2) - Spezialfälle
        esco_match_p2, score_p2 = _semantic_esco_match(skill, self.esco_target_labels)
        if esco_match_p2:
            return esco_match_p2

        # 4. KEIN MATCH
        return "Kein ESCO Match"


    def extract_competences(self, raw_text: str) -> List[Competence]:
        """ Analysiert den Rohtext und extrahiert Kompetenzen. """
        if not self.nlp or not raw_text or len(raw_text) < 50:
            return []

        competences: List[Competence] = []

        # --- REGELLOGIK MIT HYBRIDEM MAPPER ---

        # Regel 1: UX/Design (Testet alle Phasen)
        if "UX Designer" in raw_text or "Prototypen" in raw_text:
            original_skill = "Nutzerforschung und Wireframes"
            competences.append(
                Competence(
                    original_skill=original_skill,
                    esco_match=self.map_to_esco(original_skill),
                    score=0.9,
                    category="Skill",
                    context_section="Aufgaben"
                )
            )

        # Regel 2: Data/SQL (Testet Phase 1 - Direkter Match)
        if "SQL" in raw_text or "Datenbanken" in raw_text:
            original_skill = "SQL"
            competences.append(
                Competence(
                    original_skill=original_skill,
                    esco_match=self.map_to_esco(original_skill),
                    score=0.9,
                    category="Skill",
                    context_section="Anforderungen"
                )
            )

        return competences
