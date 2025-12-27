import json, os, re
PRONOUNS = {"wir","du","ihr","euch","uns","dein","mein"}
def load_esco_alias():
    p = "data/esco_alias.json"
    if os.path.exists(p):
        return json.load(open(p,"r",encoding="utf-8"))
    return {}
def extract_skills(text: str):
    if not text: return []
    aliases = load_esco_alias()
    tokens = re.findall(r"[A-Za-zÄÖÜäöüß+.#\-]{2,}", text.lower())
    out = []
    for t in tokens:
        if t in PRONOUNS: continue
        if t in aliases: out.append({"id": aliases[t], "label": t})
    seen=set(); uniq=[]
    for s in out:
        if s["id"] in seen: continue
        seen.add(s["id"]); uniq.append(s)
    return uniq