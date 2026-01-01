import os
import pypdf
import json
import re
import requests
from pathlib import Path

class ProfessionalDomainGenerator:
    def __init__(self, kotlin_url="http://localhost:8080"):
        self.kotlin_url = kotlin_url
        self.blacklist = {
            "inhalt", "vorwort", "kapitel", "literatur", "index",
            "abbildungsverzeichnis", "tabellenverzeichnis", "anhang", "impressum"
        }
        self.api_online = self._check_api()

    def _check_api(self):
        try:
            requests.get(f"{self.kotlin_url}/api/v1/rules/search-skill?query=test", timeout=1)
            return True
        except:
            print("⚠️  WARNUNG: Kotlin-Backend offline! ESCO-Brücke wird nicht geschlagen.")
            return False

    def _clean_text(self, text):
        """Höchste Reinigungsstufe für wissenschaftliche Daten."""
        if not text: return ""
        # 1. Entferne Tabulatoren und Zeilenumbrüche
        text = text.replace('\t', ' ').replace('\n', ' ')
        # 2. Heile Worttrennungen am Zeilenende (z.B. Soft- ware -> Software)
        text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)
        # 3. Entferne TOC-Punkte und Seitenzahlen am Ende
        text = re.sub(r'(\.\.\.+|\s\.+\s|\s\d+$)', '', text)
        # 4. Entferne Kapitelnummern am Anfang
        text = re.sub(r'^\d+(\.\d+)*\s+', '', text)
        # 5. Entferne Sonderzeichen wie
        text = re.sub(r'[^\w\s\-\.]', '', text)
        # 6. Doppelte Leerzeichen killen
        return re.sub(r'\s+', ' ', text).strip()

    def _get_esco_data(self, term):
        """Holt URI und das offizielle Label (Preferred Label) von ESCO via Kotlin."""
        if not self.api_online: return None, None
        try:
            response = requests.get(f"{self.kotlin_url}/api/v1/rules/search-skill", params={"query": term}, timeout=2)
            if response.status_code == 200:
                res = response.json()
                return res.get("esco_uri"), res.get("preferred_label")
        except: return None, None
        return None, None

    def process_pdf(self, pdf_path, level):
        file_name = os.path.basename(pdf_path)
        print(f"🔍 Analysiere: {file_name} (Ebene {level})")

        reader = pypdf.PdfReader(pdf_path)
        competences = []
        seen = set()

        # Scanne die ersten 25 Seiten für das Inhaltsverzeichnis
        for i in range(min(25, len(reader.pages))):
            page_text = reader.pages[i].extract_text()
            if not page_text: continue

            for line in page_text.split('\n'):
                # TOC-Erkennung: Hat Punkte oder fängt mit Nummer an
                if "..." in line or re.match(r'^\d', line.strip()):
                    title = self._clean_text(line)

                    if len(title) > 5 and title.lower() not in self.blacklist:
                        if title.lower() not in seen:
                            uri, pref_label = self._get_esco_data(title)

                            competences.append({
                                "name": pref_label if pref_label else title,
                                "original_chapter": title,
                                "level": level,
                                "esco_uri": uri if uri else f"custom/lvl{level}/{title.lower().replace(' ', '_')}",
                                "source": file_name,
                                "is_standardized": True if uri else False
                            })
                            seen.add(title.lower())

        self._save(file_name, level, competences)

    def _save(self, file_name, level, competences):
        domain = file_name.replace(".pdf", "").replace("_", " ")
        output = {
            "domain": domain,
            "level": level,
            "count": len(competences),
            "competences": competences
        }
        os.makedirs("data/job_domains", exist_ok=True)
        path = f"data/job_domains/{file_name.lower().replace('.pdf', '.json')}"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON gespeichert: {path}")

if __name__ == "__main__":
    gen = ProfessionalDomainGenerator()
    # Verarbeite beide Quellen
    mapping = {
        "data/source_pdfs/fachbuecher": 4,
        "data/source_pdfs/modulhandbuecher": 5
    }
    for folder, lvl in mapping.items():
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.endswith(".pdf"):
                    gen.process_pdf(os.path.join(folder, f), lvl)
