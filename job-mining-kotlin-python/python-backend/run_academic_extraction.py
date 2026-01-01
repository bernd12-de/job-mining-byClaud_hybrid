import os
import pypdf
import json
import re

class ProfessionalAcademicExtractor:
    def __init__(self):
        # Strenge Blacklist gegen administrative Begriffe (besonders für Ebene 5)
        self.blacklist = {
            "seite", "kapitel", "abbildung", "tabelle", "vorwort", "inhalt",
            "anhang", "literatur", "index", "isbn", "verlag", "auflage",
            "inhaltsverzeichnis", "herausgeber", "autor", "copyright",
            "modul", "semester", "studiengang", "prüfung", "note", "ects",
            "leistungspunkte", "modulverantwortliche", "turnus", "dauer"
        }

    def _is_toc_page(self, text):
        """Identifiziert TOC-Seiten anhand von Markern in den ersten 600 Zeichen."""
        if not text: return False
        head = text[:600].lower()
        return any(kw in head for kw in ["inhalt", "contents", "verzeichnis", "table of"])

    def _clean_text(self, text):
        """Entfernt Artefakte, Punktreihen und Seitenzahlen."""
        if not text: return ""
        # 1. Steuerzeichen und Tabulatoren entfernen
        text = text.replace('\t', ' ').replace('\x00', '').replace('\r', ' ')
        # 2. Worttrennungen am Zeilenende heilen
        text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)
        # 3. Punktreihen und Seitenzahlen am Ende entfernen (z.B. "Logistik ... 12")
        text = re.sub(r'(\.\.\.+|\s\.+\s|\s\d+$)', '', text)
        # 4. Kapitelnummern am Anfang entfernen (z.B. 1.2.1)
        text = re.sub(r'^\d+(\.\d+)*\s+', '', text)
        return text.strip()

    def _is_valid_academic_term(self, term):
        """Der wissenschaftliche Qualitäts-Filter (max. 4 Wörter, Nomen-Fokus)."""
        words = term.split()
        # Nur Begriffe mit 1-4 Wörtern (verhindert Satzfragmente)
        if not (1 <= len(words) <= 4): return False
        # Muss mit Großbuchstabe beginnen
        if not term[0].isupper(): return False
        # Keine Sätze (kein Punkt am Ende)
        if term.endswith(('.', ':', '?', '!')): return False
        # Keine reinen Zahlen oder URLs
        if re.search(r'(http|www|\d{3}-\d)', term.lower()): return False
        return True

    def process_pdf(self, pdf_path, level):
        file_name = os.path.basename(pdf_path)
        print(f"📖 Verarbeite {file_name} (Ebene {level})...")

        try:
            reader = pypdf.PdfReader(pdf_path)
            competences = []
            seen = set()

            # Scan der ersten 35 Seiten (Modulhandbücher haben oft lange Vorworte)
            for i in range(min(35, len(reader.pages))):
                page_text = reader.pages[i].extract_text()
                if not self._is_toc_page(page_text): continue

                for line in page_text.split('\n'):
                    cleaned = self._clean_text(line)

                    if self._is_valid_academic_term(cleaned) and cleaned.lower() not in self.blacklist:
                        if cleaned.lower() not in seen:
                            # Beibehaltung deiner detaillierten Struktur
                            competences.append({
                                "name": cleaned,
                                "original_chapter": cleaned,
                                "level": level,
                                "category": "Kapitelstruktur" if level == 4 else "Modulstruktur",
                                "type": "topic_cluster",
                                "source": file_name,
                                "esco_uri": f"custom/lvl{level}/{cleaned.lower().replace(' ', '_')}"
                            })
                            seen.add(cleaned.lower())

            self._save(file_name, level, competences)
            return len(competences)
        except Exception as e:
            print(f"❌ Fehler bei {file_name}: {e}")
            return 0

    def _save(self, filename, level, competences):
        os.makedirs("data/job_domains", exist_ok=True)
        safe_name = re.sub(r'\W+', '_', filename.lower().replace('.pdf', ''))
        path = f"data/job_domains/{safe_name}.json"

        output = {
            "domain": filename.replace('.pdf', '').replace('_', ' '),
            "level": level,
            "count": len(competences),
            "competences": competences
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"   ✅ {len(competences)} saubere Begriffe gespeichert.")

def run_batch():
    extractor = ProfessionalAcademicExtractor()
    paths = {
        "data/source_pdfs/fachbuecher": 4,
        "data/source_pdfs/modulhandbuecher": 5
    }
    for folder, level in paths.items():
        if os.path.exists(folder):
            print(f"\n📂 Starte Batch für Ebene {level}...")
            for f in os.listdir(folder):
                if f.endswith(".pdf"):
                    extractor.process_pdf(os.path.join(folder, f), level)

if __name__ == "__main__":
    run_batch()
