import pypdf
import json
import re
import os
from pathlib import Path

class SmartDomainGenerator:
    def __init__(self, blacklist=None):
        self.blacklist = blacklist or {
            "seite", "kapitel", "abbildung", "tabelle", "vorwort",
            "inhalt", "anhang", "literatur", "index", "isbn", "verlag"
        }
        # Suchbegriffe für die Sektions-Erkennung
        self.marker_toc = ["inhaltsverzeichnis", "inhalt", "table of contents", "contents"]
        self.marker_glossary = ["glossar", "glossary", "stichwortverzeichnis", "index", "begriffsglossar"]

    def _find_pages_by_keywords(self, reader, keywords):
        """Sucht Seiten, die eines der Schlüsselwörter prominent (oben) enthalten."""
        found_pages = []
        # Wir suchen TOC am Anfang (erste 15 Seiten), Glossar am Ende (letzte 30 Seiten)
        search_range = range(len(reader.pages))

        for i in search_range:
            try:
                # Wir laden nur die ersten 500 Zeichen der Seite für die Erkennung (Performance)
                head_text = reader.pages[i].extract_text()[:500].lower()
                if any(kw in head_text for kw in keywords):
                    found_pages.append(i)
            except:
                continue
        return found_pages

    def process_pdf_auto(self, pdf_path, domain_name, level):
        print(f"🔍 Automatische Analyse: {os.path.basename(pdf_path)}")
        try:
            reader = pypdf.PdfReader(pdf_path)

            # 1. Sektionen finden
            toc_pages = self._find_pages_by_keywords(reader, self.marker_toc)
            # Glossar ist meist ganz hinten, daher filtern wir die Suche
            all_potential_glossaries = self._find_pages_by_keywords(reader, self.marker_glossary)
            glossary_pages = [p for p in all_potential_glossaries if p > len(reader.pages) * 0.7]

            print(f"   -> Gefundene Inhaltsseiten: {toc_pages}")
            print(f"   -> Gefundene Glossarseiten: {glossary_pages}")

            # 2. Extraktion
            competences = []
            seen = set()

            # Wir lesen TOC und Glossar aus
            for p_num in (toc_pages + glossary_pages):
                text = reader.pages[p_num].extract_text()
                # Fachbegriffe extrahieren (Großbuchstabe, mind. 5 Zeichen)
                words = re.findall(r'\b[A-ZÄÖÜ][a-zäöüß-]{4,25}\b', text)

                for w in words:
                    w_low = w.lower()
                    if w_low not in self.blacklist and w_low not in seen:
                        section = "Glossar" if p_num in glossary_pages else "Inhalt"
                        competences.append({
                            "name": w,
                            "level": level,
                            "source_section": section,
                            "confidence": 0.95 if section == "Glossar" else 0.8,
                            "source_file": os.path.basename(pdf_path)
                        })
                        seen.add(w_low)

            self._save_json(domain_name, level, competences)

        except Exception as e:
            print(f"   ❌ Fehler: {e}")

    def _save_json(self, name, level, competences):
        output = {
            "domain": name,
            "level": level,
            "count": len(competences),
            "competences": competences
        }
        os.makedirs("data/job_domains", exist_ok=True)
        filename = f"data/job_domains/{name.lower().replace(' ', '_')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"   ✅ {len(competences)} Begriffe gespeichert in {filename}")
