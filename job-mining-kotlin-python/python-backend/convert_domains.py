#!/usr/bin/env python3
"""
Konvertiert die generierten Domain-Listen ins Repository-kompatible Format.
"""
import json
from pathlib import Path

def convert_domain(input_file: str, output_file: str, domain_name: str, level: int):
    """Konvertiert eine Liste von Keywords in das Domain-Format."""
    print(f"📝 Konvertiere {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        keywords = json.load(f)
    
    # Filter: Nur relevante Begriffe (>3 Zeichen, keine Abkürzungen in Kleinschreibung)
    filtered = []
    for keyword in keywords:
        if len(keyword) > 3 and not keyword.isupper():
            filtered.append(keyword)
    
    print(f"  ✅ {len(filtered)} von {len(keywords)} Begriffen gefiltert")
    
    # Erstelle Competence-Objekte
    competences = []
    for kw in filtered[:5000]:  # Limitiere auf 5000 relevanteste
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
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(domain, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Domain gespeichert: {output_path} ({len(competences)} Kompetenzen)")

if __name__ == "__main__":
    # Ebene 4: Fachbücher
    convert_domain(
        "data/job_domains/fachbuch_domain.json",
        "data/job_domains/fachbuch_domain_formatted.json",
        "Fachbuch Domain (Softwarearchitektur & Microservices)",
        4
    )
    
    # Ebene 5: Academia
    convert_domain(
        "data/job_domains/academia_domain.json",
        "data/job_domains/academia_domain_formatted.json",
        "Akademische Domain (Modulhandbücher)",
        5
    )
    
    print("\n✅ Konvertierung abgeschlossen!")
    print("Die formatierten Domains können jetzt vom HybridCompetenceRepository geladen werden.")
