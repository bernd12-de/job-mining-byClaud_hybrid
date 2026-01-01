import json, os, re

# ✅ Bereinigte Blacklist: Nur wirklich generische Begriffe
# ENTFERNT: r, management, analyse, strategie, informatik, digitalisierung, projektleitung, agil, prozess, technik
GENERIC_SKILLS_BLACKLIST = {
    "kenntnisse", "fähigkeiten", "kommunikation", "deutsch", "englisch",
    "bau", "ski", "sport", "medien", "wissenschaft", "erfahrung",
    "kunden", "lösung", "team", "bereich", "verantwortung übernehmen",
    "beratung", "dienstleistungen"
}
PRONOUNS = {"wir","du","ihr","euch","uns","dein","mein"}

def load_esco_alias():
    p = "data/esco_alias.json"
    if os.path.exists(p):
        return json.load(open(p,"r",encoding="utf-8"))
    print("⚠️ WARNUNG: esco_alias.json nicht gefunden.")
    return {}

def extract_skills(text: str):
    """ Extrahiert Skills mit Aliasing und Eliminiert ESCO-Rauschen. """
    if not text: return []
    aliases = load_esco_alias()
    # ✅ KERN-FIX: Mindestens 2 Zeichen, erlaubt R, C, Go
    tokens = re.findall(r"[A-Za-zÄÖÜäöüß+.#\-]{2,}", text.lower())

    out = []
    for t in tokens:
        # 1. Pronomen-Filter
        if t in PRONOUNS: continue

        # 2. BLACKLIST-FILTER (KERN-FIX)
        if t in GENERIC_SKILLS_BLACKLIST: continue

        # 3. Alias-Check
        if t in aliases:
            mapped_label = aliases[t].lower()
            if mapped_label in GENERIC_SKILLS_BLACKLIST: continue

            # Das ist die ursprüngliche Speicherung
            out.append({"id": aliases[t], "label": t})

    # Deduplizierung
    seen=set(); uniq=[]
    for s in out:
        if s["id"] in seen: continue
        seen.add(s["id"]); uniq.append(s)

    return uniq
