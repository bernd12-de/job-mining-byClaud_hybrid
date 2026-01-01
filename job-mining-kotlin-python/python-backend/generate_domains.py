import pypdf
import json
import re
from pathlib import Path

def extract_from_dir(directory: str, output_filename: str, domain_name: str, level: int):
    """
    Extrahiert Fachbegriffe aus PDFs und speichert sie als Domain im Repository-Format.
    
    Args:
        directory: Pfad zum PDF-Verzeichnis
        output_filename: Name der JSON-Ausgabedatei (ohne .json)
        domain_name: Name der Domain
        level: ESCO-Level (4 = Fachbuch, 5 = Academia)
    """
    print(f"📂 Scanne Verzeichnis: {directory}...")
    keywords = set()
    path = Path(directory)

    if not path.exists():
        print(f"⚠️ Pfad nicht gefunden: {directory}")
        return

    for pdf_file in path.glob("*.pdf"):
        print(f"  📄 Lese {pdf_file.name}...")
        try:
            reader = pypdf.PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    # Sucht nach Fachbegriffen (Substantive, Komposita)
                    found = re.findall(r'\b[A-ZÄÖÜ][a-zäöüß-]{3,25}\b', text)
                    keywords.update([f.lower() for f in found])
        except Exception as e:
            print(f"  ❌ Fehler bei {pdf_file.name}: {e}")

    # Filter: Nur relevante Begriffe
    filtered = [kw for kw in keywords if len(kw) > 3 and not kw.isupper()]
    print(f"  ✅ {len(filtered)} von {len(keywords)} Begriffen gefiltert")
    
    # Limitiere auf 5000 relevanteste Skills
    filtered = sorted(filtered)[:5000]
    
    # Erstelle Competence-Objekte im Repository-Format
    competences = []
    for kw in filtered:
        competences.append({
            "name": kw.capitalize(),
            "category": "Extracted",
            "type": "skill",
            "level": level
        })
    
    # Domain-Objekt erstellen
    domain = {
        "domain": domain_name,
        "level": level,
        "source": "Generated from PDFs",
        "competences": competences
    }
    
    # Speichern
    output_path = Path(f"data/job_domains/{output_filename}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(domain, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Domain gespeichert unter: {output_path} ({len(competences)} Kompetenzen)")

if __name__ == "__main__":
    print("🚀 Domain-Generierung gestartet...\n")
    
    # Ebene 4: Fachbücher (Gharbi, Wolff, Spillner)
    extract_from_dir(
        "data/source_pdfs/fachbuecher",
        "fachbuch_domain",
        "Fachbuch Domain (Softwarearchitektur & Microservices)",
        4
    )

    # Ebene 5: Modulhandbücher (Hochschule/Uni)
    extract_from_dir(
        "data/source_pdfs/modulhandbuecher",
        "academia_domain",
        "Akademische Domain (Modulhandbücher)",
        5
    )
    
    print("\n✅ Domain-Generierung abgeschlossen!")
    print("Die Domains können jetzt vom HybridCompetenceRepository geladen werden.")

