from collections import Counter
import re

STOPWORDS = {"und", "oder", "der", "die", "das", "mit", "ein", "eine", "auf", "in", "zu", "für", "von", "am"}

def extract_keywords(text, top_n=15):
    tokens = re.findall(r'\b\w+\b', text)
    filtered = [t for t in tokens if len(t) > 3 and t not in STOPWORDS]
    freq = Counter(filtered)
    return [w for w, _ in freq.most_common(top_n)]
