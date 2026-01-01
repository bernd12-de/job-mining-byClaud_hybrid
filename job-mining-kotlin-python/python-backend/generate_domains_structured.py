import pypdf
import json
import re
from pathlib import Path

# Diese Wörter wollen wir NICHT in unseren Kompetenz-Listen
BLACKLIST = {"seite", "kapitel", "abbildung", "tabelle", "verfasser", "anja", "inhalt", "vorwort"}

def build_structured_domain(source_path: str, domain_name: str, level: int):
    print(f"🛠️ Erstelle Ebene {level} für {domain_name} aus {source_path}...")
    keywords = set()

    path = Path(source_path)
    for pdf_file in path.glob("*.pdf"):
        reader = pypdf.PdfReader(pdf_file)
        for page in reader.pages:
            text = page.extract_text()
            # Finde Begriffe: Großbuchstabe am Anfang, mind. 5 Zeichen
            found = re.findall(r'\b[A-ZÄÖÜ][a-zäöüß-]{4,25}\b', text)
            for f in found:
                if f.lower() not in BLACKLIST:
                    keywords.add(f)

    # Struktur an deine 'agile_methods.json' anpassen
    structured_data = {
        "domain": domain_name,
        "level": level,
        "competences": [
            {
                "name": kw,
                "category": "Extracted",
                "type": "skill",
                "confidence": 0.7  # PDF-Extraktion ist unsicherer als händische Listen
            } for kw in sorted(list(keywords))
        ]
    }

    output_path = Path(f"data/job_domains/{domain_name.lower().replace(' ', '_')}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Datei gespeichert: {output_path} ({len(keywords)} Begriffe)")

if __name__ == "__main__":
    # Jetzt gezielt nach deinen Ordnern trennen:
    build_structured_domain("data/source_pdfs/fachbuecher", "Fachbuch Validierung", 4)
    build_structured_domain("data/source_pdfs/modulhandbuecher", "Akademisches Curriculum", 5)
