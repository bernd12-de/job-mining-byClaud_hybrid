from __future__ import annotations
import re
from typing import List

from models.job_ad import Competence, CompetenceType
from services.extraction.competence_library import CompetenceLibrary

_SPACY_AVAILABLE = False
_EMBEDDINGS_AVAILABLE = False
_NLP = None
_EMB_MODEL = None

def _init_spacy():
    global _SPACY_AVAILABLE, _NLP
    if _NLP is not None:
        return
    try:
        import spacy
        for model in ["de_core_news_md", "de_core_news_sm", "en_core_web_sm"]:
            try:
                _NLP = spacy.load(model)
                _SPACY_AVAILABLE = True
                break
            except Exception:
                continue
    except Exception:
        _SPACY_AVAILABLE = False
        _NLP = None

def _init_embeddings():
    global _EMBEDDINGS_AVAILABLE, _EMB_MODEL
    if _EMB_MODEL is not None:
        return
    try:
        from sentence_transformers import SentenceTransformer
        _EMB_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        _EMBEDDINGS_AVAILABLE = True
    except Exception:
        _EMBEDDINGS_AVAILABLE = False
        _EMB_MODEL = None

class CompetenceMatcher:
    def __init__(self, library: CompetenceLibrary, use_spacy: bool = True, use_embeddings: bool = True):
        self.lib = library
        self.use_spacy = use_spacy
        self.use_embeddings = use_embeddings

    def find(self, text: str, max_embed_candidates: int = 5, sim_threshold: float = 0.62) -> List[Competence]:
        if not text:
            return []
        lower = text.lower()
        found_names = set()

        # 1) Regex/dictionary
        for key in self.lib.keys_for_matching():
            if re.search(rf"\b{re.escape(key)}\b", lower):
                canonical = self.lib.lookup_canonical(key)
                if canonical:
                    found_names.add(canonical)

        # 2) spaCy heuristics
        if self.use_spacy:
            _init_spacy()
            if _SPACY_AVAILABLE:
                try:
                    doc = _NLP(text[:10000])
                    tokens = set([t.text for t in doc if t.pos_ in ("PROPN", "NOUN") and len(t.text) > 2])
                    for tok in tokens:
                        lk = tok.lower()
                        canon = self.lib.lookup_canonical(lk)
                        if canon:
                            found_names.add(canon)
                except Exception:
                    pass

        # 3) Embeddings
        if self.use_embeddings:
            _init_embeddings()
            if _EMBEDDINGS_AVAILABLE:
                try:
                    from numpy import dot
                    from numpy.linalg import norm
                    names = list(set(self.lib.keys_for_matching()))[:500]
                    vt = _EMB_MODEL.encode([text[:1500]])[0]
                    pool = names[:1500]
                    name_vectors = _EMB_MODEL.encode(pool, batch_size=64, show_progress_bar=False)
                    sims = []
                    for name, vec in zip(pool, name_vectors):
                        s = float(dot(vt, vec) / (norm(vt)*norm(vec) + 1e-9))
                        sims.append((name, s))
                    sims.sort(key=lambda x: x[1], reverse=True)
                    for name, score in sims[:max_embed_candidates]:
                        canon = self.lib.lookup_canonical(name)
                        if canon and score >= sim_threshold:
                            found_names.add(canon)
                except Exception:
                    pass

        results: List[Competence] = []
        for n in sorted(found_names):
            meta = self.lib.meta(n)
            ctype = (meta.get("type") or "skill").lower()
            type_map = {
                "tool": CompetenceType.TOOL,
                "method": CompetenceType.METHOD,
                "framework": CompetenceType.FRAMEWORK,
                "language": CompetenceType.LANGUAGE,
                "platform": CompetenceType.PLATFORM,
                "knowledge": CompetenceType.KNOWLEDGE,
                "attitude": CompetenceType.ATTITUDE,
                "skill": CompetenceType.SKILL,
                "technology": CompetenceType.TECHNOLOGY,
            }
            results.append(Competence(
                name=n,
                category=meta.get("category") or "General",
                competence_type=type_map.get(ctype, CompetenceType.SKILL),
                esco_uri=meta.get("uri") or "",
                alternative_labels=meta.get("alternative_labels") or [],
                confidence_score=1.0,
                source="stepwise_matcher",
                context_snippet=""
            ))
        return results
