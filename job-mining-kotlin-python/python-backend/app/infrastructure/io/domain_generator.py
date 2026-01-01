import os
import pypdf
import json
import re
import requests
from pathlib import Path

class StructuralDomainGenerator:
    """Extrahiert Begriffe aus Fachbüchern und validiert sie gegen ESCO."""

    def __init__(self, kotlin_url="http://localhost:8080"):
        self.kotlin_url = kotlin_url
        self.blacklist = {"seite", "kapitel", "abbildung", "tabelle", "inhalt", "vorwort"}

    def process_pdf_to_domain(self, pdf_path: str, level: int):
        file_name = os.path.basename(pdf_path)
        domain_name = file_name.replace(".pdf", "").replace("_", " ")
        competences = []
        seen = set()

        try:
            reader = pypdf.PdfReader(pdf_path)
            # Analysiere alle Seiten (TOC und Glossar haben Priorität)
            for page in reader.pages:
                text = page.extract_text()
                # Fachbegriffe finden (Großbuchstabe, 4-25 Zeichen)
                found = re.findall(r'\b[A-ZÄÖÜ][a-zäöüß-]{3,25}\b', text)

                for term in found:
                    term_low = term.lower()
                    if term_low not in self.blacklist and term_low not in seen:
                        # WICHTIG: Prüfe gegen die 31.655 ESCO-Labels
                        is_std = self._check_esco_standard(term)

                        if not is_std: # Nur Begriffe aufnehmen, die NEU sind (Ebene 4/5 Innovation)
                            competences.append({
                                "name": term,
                                "level": level,
                                "source": file_name,
                                "is_discovery": True if level == 5 else False
                            })
                            seen.add(term_low)

            self._save_json(domain_name, level, competences)
        except Exception as e:
            print(f"❌ Fehler bei {file_name}: {e}")

    def _check_esco_standard(self, query):
        """Fragt das Kotlin-Backend (SSoT), ob der Begriff Standard ist."""
        try:
            # Endpunkt muss in Kotlin RuleController existieren
            res = requests.get(f"{self.kotlin_url}/api/v1/rules/search-skill", params={"query": query}, timeout=2)
            return res.status_code == 200 # 200 = Gefunden (Ebene 2)
        except:
            return False

    def _save_json(self, name, level, competences):
        os.makedirs("data/job_domains", exist_ok=True)
        safe_name = name.lower().replace(" ", "_")
        path = f"data/job_domains/{safe_name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"domain": name, "level": level, "competences": competences}, f, ensure_ascii=False, indent=2)
        print(f"✅ Domäne für Ebene {level} erstellt: {path} ({len(competences)} Begriffe)")
