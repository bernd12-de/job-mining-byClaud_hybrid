import re, collections
from .skill_filter import extract_skills
def top_keywords(texts, k=10):
    cnt = collections.Counter()
    for t in texts:
        for w in re.findall(r"[A-Za-zÄÖÜäöüß]{3,}", t.lower()):
            if w in {"und","oder","die","der","das","mit","für","bei"}: continue
            cnt[w]+=1
    return cnt.most_common(k)
def get_fields(texts):
    kws = dict(top_keywords(texts, k=50))
    fields = {}
    if any("digital" in k for k in kws): fields.setdefault("categories", []).append("Digitalisierung")
    if any(("data" in k) or ("daten" in k) for k in kws): fields.setdefault("categories", []).append("Daten")
    skills = []
    for t in texts: skills.extend(extract_skills(t))
    fields["skills_esco"] = skills
    return fields