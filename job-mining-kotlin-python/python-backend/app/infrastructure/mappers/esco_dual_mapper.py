"""
ESCO Dual-Mapping v2.0
======================

✅ BEST PRACTICE: Multi-Methode ESCO-Matching

Kombiniert 3 Matching-Methoden:
1. RapidFuzz - Token-basiertes Fuzzy Matching
2. MiniLM - Semantic Similarity (English)
3. MultiLM - Semantic Similarity (Multilingual, Deutsch)

Features:
- Automatische Best-Match Auswahl
- Confidence Scoring pro Match
- Multilingual Support (Deutsch + English)
- Performance-optimiert

Basiert auf: Best_Practice Code Lib/nlp_extraction/esco_mapper_dual.py
"""

import logging
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class EscoDualMapper:
    """
    ✅ BEST PRACTICE: Dual-Methode ESCO Mapper

    Verwendet 3 Matching-Strategien:
    - RapidFuzz: Fuzzy String Matching
    - MiniLM: Semantic Similarity (fast)
    - MultiLM: Multilingual Semantic Similarity

    Wählt automatisch beste Methode pro Skill.
    """

    def __init__(self):
        """
        Initialize Mapper mit Dependency Checks
        """
        self._check_dependencies()
        logger.info("EscoDualMapper initialized")

    def _check_dependencies(self):
        """Prüft verfügbare Bibliotheken"""
        # RapidFuzz
        try:
            from rapidfuzz import fuzz
            self.rapidfuzz_available = True
            self.fuzz = fuzz
        except ImportError:
            logger.warning("RapidFuzz not available. Install: pip install rapidfuzz")
            self.rapidfuzz_available = False
            self.fuzz = None

        # SentenceTransformers (ML Models)
        try:
            from sentence_transformers import SentenceTransformer, util
            self.transformers_available = True

            # Load Models (lazy loading möglich)
            try:
                self.model_mini = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                self.model_multi = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
                self.util = util
                logger.info("✅ SentenceTransformers loaded (Models: ~500MB)")
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer models: {e}")
                self.transformers_available = False

        except ImportError:
            logger.warning("SentenceTransformers not available.")
            logger.warning("Install: pip install sentence-transformers")
            logger.warning("Note: Downloads ~500MB models on first use")
            self.transformers_available = False

    def map_skills_dual(self, keywords: List[str], esco_skills: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        ✅ BEST PRACTICE: Dual-Methode Skill-Mapping

        Args:
            keywords: Liste von Skills zum Mappen
            esco_skills: ESCO Skills (Format: [{'label': 'Python', ...}, ...])

        Returns:
            Tuple[mapped_results, comparison_data]
            - mapped_results: Detaillierte Matches mit allen Scores
            - comparison_data: Vereinfachte Vergleichsdaten
        """
        if not esco_skills:
            logger.warning("Keine ESCO Skills bereitgestellt")
            return [], []

        logger.info(f"Mapping {len(keywords)} Keywords gegen {len(esco_skills)} ESCO Skills")

        mapped = []
        comparison = []

        # Pre-compute Embeddings (Performance-Optimierung)
        esco_texts = [s.get('label', s.get('preferredLabel', '')) for s in esco_skills]
        esco_emb_mini = None
        esco_emb_multi = None

        if self.transformers_available:
            try:
                esco_emb_mini = self.model_mini.encode(esco_texts, convert_to_tensor=True, show_progress_bar=False)
                esco_emb_multi = self.model_multi.encode(esco_texts, convert_to_tensor=True, show_progress_bar=False)
            except Exception as e:
                logger.warning(f"Embedding computation failed: {e}")

        # Map jeden Keyword
        for kw in keywords:
            result = self._map_single_keyword(kw, esco_skills, esco_texts, esco_emb_mini, esco_emb_multi)
            mapped.append(result['mapped'])
            comparison.append(result['comparison'])

        logger.info(f"✅ Mapping complete: {len(mapped)} results")
        return mapped, comparison

    def _map_single_keyword(self, kw: str, esco_skills: List[Dict], esco_texts: List[str],
                           esco_emb_mini, esco_emb_multi) -> Dict:
        """
        Mappt einzelnen Keyword mit allen Methoden

        Returns:
            Dict mit 'mapped' und 'comparison' keys
        """
        # METHODE 1: RapidFuzz (Fuzzy Matching)
        fuzz_score = 0
        best_fuzz = None

        if self.rapidfuzz_available:
            try:
                scores = [(skill, self.fuzz.token_set_ratio(kw, esco_texts[i]))
                         for i, skill in enumerate(esco_skills)]
                best_fuzz = max(scores, key=lambda x: x[1])
                fuzz_score = best_fuzz[1]
            except Exception as e:
                logger.warning(f"RapidFuzz matching failed: {e}")

        # METHODE 2: MiniLM (Semantic - English)
        sim_mini = 0.0
        if self.transformers_available and esco_emb_mini is not None:
            try:
                kw_emb_mini = self.model_mini.encode(kw, convert_to_tensor=True)
                sim_mini = self.util.cos_sim(kw_emb_mini, esco_emb_mini).max().item()
            except Exception as e:
                logger.warning(f"MiniLM matching failed: {e}")

        # METHODE 3: MultiLM (Semantic - Multilingual)
        sim_multi = 0.0
        if self.transformers_available and esco_emb_multi is not None:
            try:
                kw_emb_multi = self.model_multi.encode(kw, convert_to_tensor=True)
                sim_multi = self.util.cos_sim(kw_emb_multi, esco_emb_multi).max().item()
            except Exception as e:
                logger.warning(f"MultiLM matching failed: {e}")

        # AUSWAHL: Beste Methode
        # Fuzzy Score ist 0-100, Semantic ist 0-1
        # Normalisiere für Vergleich
        best_model = self._select_best_model(fuzz_score, sim_mini, sim_multi)

        mapped_result = {
            "keyword": kw,
            "rapidfuzz": {
                "match": esco_texts[esco_skills.index(best_fuzz[0])] if best_fuzz else "",
                "score": fuzz_score
            },
            "miniLM": {"score": round(sim_mini, 3)},
            "multiLM": {"score": round(sim_multi, 3)},
            "best_model": best_model,
            "confidence": self._calculate_confidence(fuzz_score, sim_mini, sim_multi, best_model)
        }

        comparison_result = {
            "keyword": kw,
            "rapidfuzz": fuzz_score,
            "miniLM": sim_mini,
            "multiLM": sim_multi,
            "best_model": best_model
        }

        return {'mapped': mapped_result, 'comparison': comparison_result}

    def _select_best_model(self, fuzz_score: float, sim_mini: float, sim_multi: float) -> str:
        """
        Wählt beste Methode basierend auf Scores

        Logic:
        - Wenn Fuzzy > 90: Fuzzy ist sehr sicher
        - Wenn Fuzzy < 70 und Semantic > 0.8: Semantic ist besser
        - Sonst: Höchster Score gewinnt
        """
        # Normalisiere Scores (0-1 range)
        norm_fuzz = fuzz_score / 100.0
        norm_mini = sim_mini
        norm_multi = sim_multi

        # High confidence Fuzzy
        if fuzz_score > 90:
            return 'rapidfuzz'

        # Low Fuzzy, high Semantic
        if fuzz_score < 70 and (sim_mini > 0.8 or sim_multi > 0.8):
            return 'miniLM' if sim_mini > sim_multi else 'multiLM'

        # Höchster Score
        scores = {'rapidfuzz': norm_fuzz, 'miniLM': norm_mini, 'multiLM': norm_multi}
        return max(scores, key=scores.get)

    def _calculate_confidence(self, fuzz_score: float, sim_mini: float, sim_multi: float, best_model: str) -> float:
        """
        Berechnet Confidence Score (0-1)

        Basiert auf:
        - Score der besten Methode
        - Übereinstimmung zwischen Methoden
        """
        # Normalisiere
        norm_fuzz = fuzz_score / 100.0
        norm_mini = sim_mini
        norm_multi = sim_multi

        # Basis-Confidence: Score der besten Methode
        scores = {'rapidfuzz': norm_fuzz, 'miniLM': norm_mini, 'multiLM': norm_multi}
        base_confidence = scores[best_model]

        # Bonus für Übereinstimmung zwischen Methoden
        agreement_bonus = 0.0
        if norm_fuzz > 0.7 and norm_mini > 0.7:
            agreement_bonus += 0.1
        if norm_mini > 0.7 and norm_multi > 0.7:
            agreement_bonus += 0.1

        confidence = min(1.0, base_confidence + agreement_bonus)
        return round(confidence, 3)

    def get_best_match(self, keyword: str, esco_skills: List[Dict]) -> Optional[Dict]:
        """
        Convenience Methode: Liefert besten Match für einzelnen Keyword

        Args:
            keyword: Skill zum Mappen
            esco_skills: ESCO Skills

        Returns:
            Best Match oder None
        """
        mapped, _ = self.map_skills_dual([keyword], esco_skills)

        if mapped:
            return mapped[0]
        return None
