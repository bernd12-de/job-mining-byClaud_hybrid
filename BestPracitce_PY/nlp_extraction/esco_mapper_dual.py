from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer, util
import torch

model_mini = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
model_multi = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

def map_skills_dual(keywords, esco_skills):
    mapped, comparison = [], []
    esco_texts = [s['label'] for s in esco_skills]
    esco_emb_mini = model_mini.encode(esco_texts, convert_to_tensor=True, show_progress_bar=False)
    esco_emb_multi = model_multi.encode(esco_texts, convert_to_tensor=True, show_progress_bar=False)

    for kw in keywords:
        best_fuzz = max(esco_skills, key=lambda s: fuzz.token_set_ratio(kw, s['label']))
        fuzz_score = fuzz.token_set_ratio(kw, best_fuzz['label'])

        kw_emb_mini = model_mini.encode(kw, convert_to_tensor=True)
        kw_emb_multi = model_multi.encode(kw, convert_to_tensor=True)
        sim_mini = util.cos_sim(kw_emb_mini, esco_emb_mini).max().item()
        sim_multi = util.cos_sim(kw_emb_multi, esco_emb_multi).max().item()

        best_model = 'rapidfuzz' if fuzz_score > (sim_mini*100) and fuzz_score > (sim_multi*100) else ('miniLM' if sim_mini > sim_multi else 'multiLM')

        mapped.append({
            "keyword": kw,
            "rapidfuzz": {"match": best_fuzz['label'], "score": fuzz_score},
            "miniLM": {"score": round(sim_mini,3)},
            "multiLM": {"score": round(sim_multi,3)},
            "best_model": best_model
        })
        comparison.append({"keyword": kw, "rapidfuzz": fuzz_score, "miniLM": sim_mini, "multiLM": sim_multi, "best_model": best_model})
    return mapped, comparison
