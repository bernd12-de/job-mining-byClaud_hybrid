"""
Domain Extractor: Metadata Extractor mit Aufgaben-Extraktion
Extrahiert: Firma, Ort, Jahr, Titel, Aufgaben, Requirements
"""

import re
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class JobMetadata:
    """Alle Metadaten einer Stellenanzeige"""
    job_title: Optional[str] = None
    organization: Optional[str] = None
    location: Optional[str] = None
    year: Optional[int] = None
    remote: Optional[bool] = None
    job_type: Optional[str] = None
    job_category: Optional[str] = None
    
    # NEU: Aufgaben & Anforderungen
    tasks: List[str] = None  # Was wird gemacht?
    requirements: List[str] = None  # Was wird gebraucht?
    
    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []
        if self.requirements is None:
            self.requirements = []


class MetadataExtractor:
    """
    Extrahiert Metadaten aus Stellenanzeigen
    
    NEU: Extrahiert auch Aufgaben & Anforderungen!
    """
    
    def __init__(self):
        # Aufgaben-Patterns
        self.task_headers = [
            r'(?:Deine\s+)?Aufgaben',
            r'(?:Deine\s+)?Tätigkeiten',
            r'Was\s+dich\s+erwartet',
            r'Aufgabengebiet',
            r'Responsibilities',
            r'Your\s+(?:main\s+)?tasks',
            r'Was\s+du\s+(?:bei\s+uns\s+)?machst',
            r'Dein\s+Wirkungskreis',
        ]
        
        # Anforderungs-Patterns
        self.requirement_headers = [
            r'(?:Dein\s+)?Profil',
            r'(?:Das\s+)?Anforderungen?',
            r'Was\s+du\s+mitbringst',
            r'(?:Das\s+)?bringst\s+du\s+mit',
            r'Requirements?',
            r'Qualifications?',
            r'Was\s+wir\s+(?:uns\s+)?wünschen',
            r'Deine\s+Qualifikation',
        ]
        
        # Firmen-Patterns
        self.organization_patterns = [
            r'(?:bei|@)\s+([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+){0,3})\s+(?:GmbH|AG|SE|e\.V\.|Inc)',
            r'([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+){0,3})\s+(?:GmbH|AG|SE)',
        ]
        
        # Orts-Patterns (deutsche Städte)
        self.location_keywords = [
            'Berlin', 'München', 'Hamburg', 'Köln', 'Frankfurt',
            'Stuttgart', 'Düsseldorf', 'Dortmund', 'Essen', 'Leipzig',
            'Bremen', 'Dresden', 'Hannover', 'Nürnberg', 'Duisburg',
            'Karlsruhe', 'Mannheim', 'Wiesbaden', 'Münster', 'Bonn'
        ]
    
    def extract_all(self, text: str, filename: Optional[str] = None) -> Dict:
        """Extrahiere ALLE Metadaten inkl. Gehalt, Erfahrung, Bildung (Stufe 3)"""
        salary = self._extract_salary(text)
        experience = self._extract_experience(text)
        
        return {
            'job_title': self._extract_title(text, filename),
            'organization': self._extract_organization(text),
            'location': self._extract_location(text),
            'year': self._extract_year(text, filename),
            'remote': self._check_remote(text),
            'job_type': self._extract_job_type(text),
            'job_category': self._infer_job_category(text),
            'tasks': self._extract_tasks(text),
            'requirements': self._extract_requirements(text),
            # NEU: Stufe 3 Metadaten
            'salary_min': salary[0],
            'salary_max': salary[1],
            'experience_years_min': experience[0],
            'experience_years_max': experience[1],
            'education_level': self._extract_education(text),
            'languages': self._extract_languages(text),
        }
    
    def _extract_tasks(self, text: str) -> List[str]:
        """
        Extrahiere Aufgaben aus Stellenanzeige
        
        Strategie:
        1. Finde "Aufgaben"-Abschnitt
        2. Extrahiere Bullet Points
        3. Säubere und normalisiere
        """
        tasks = []
        
        # Finde Aufgaben-Abschnitt
        for header_pattern in self.task_headers:
            pattern = rf'{header_pattern}\s*:?\s*(.*?)(?=(?:{"│".join(self.requirement_headers)}|$))'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            
            if match:
                section = match.group(1)
                
                # Extrahiere Bullet Points
                bullets = self._extract_bullets(section)
                
                if bullets:
                    tasks.extend(bullets)
                    break  # Ersten Match nehmen
        
        return tasks[:10]  # Max 10 Aufgaben
    
    def _extract_requirements(self, text: str) -> List[str]:
        """
        Extrahiere Anforderungen aus Stellenanzeige
        
        Analog zu Aufgaben
        """
        requirements = []
        
        # Finde Anforderungs-Abschnitt
        for header_pattern in self.requirement_headers:
            pattern = rf'{header_pattern}\s*:?\s*(.*?)(?=(?:Benefits|Wir bieten|What we offer|$))'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            
            if match:
                section = match.group(1)
                
                # Extrahiere Bullet Points
                bullets = self._extract_bullets(section)
                
                if bullets:
                    requirements.extend(bullets)
                    break
        
        return requirements[:10]  # Max 10 Anforderungen
    
    def _extract_bullets(self, section: str) -> List[str]:
        """
        Extrahiere Bullet Points aus Abschnitt
        
        Erkennt:
        - "• Item"
        - "- Item"
        - "* Item"
        - "▪ Item"
        - Nummerierte Listen: "1. Item"
        """
        bullets = []
        
        # Zeilen splitten
        lines = section.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip zu kurze Zeilen
            if len(line) < 10:
                continue
            
            # Bullet Point Patterns
            bullet_patterns = [
                r'^[•\-\*▪]\s+(.+)$',  # • - * ▪
                r'^\d+\.\s+(.+)$',      # 1. 2. 3.
                r'^[a-z]\)\s+(.+)$',    # a) b) c)
            ]
            
            for pattern in bullet_patterns:
                match = re.match(pattern, line)
                if match:
                    bullet_text = match.group(1).strip()
                    
                    # Säubere
                    bullet_text = self._clean_bullet(bullet_text)
                    
                    if bullet_text and len(bullet_text) > 15:
                        bullets.append(bullet_text)
                    break
        
        # Fallback: Wenn keine Bullets, nehme Sätze
        if not bullets:
            sentences = re.split(r'[.!?]\s+', section)
            for sent in sentences[:5]:
                sent = sent.strip()
                if 20 < len(sent) < 200:
                    bullets.append(sent)
        
        return bullets
    
    def _clean_bullet(self, text: str) -> str:
        """Säubere Bullet Point Text"""
        # Entferne führende Sonderzeichen
        text = re.sub(r'^[•\-\*▪\d\.\)\s]+', '', text)
        
        # Entferne trailing Punkte
        text = text.rstrip('.')
        
        # Normalisiere Whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _extract_title(self, text: str, filename: Optional[str] = None) -> Optional[str]:
        """Extrahiere Job-Titel (erste relevante Zeile)"""
        lines = text.split('\n')
        
        for line in lines[:20]:
            line = line.strip()
            
            if 10 < len(line) < 100:
                # Job title indicators
                job_keywords = ['Designer', 'Manager', 'Developer', 'Engineer', 
                               'Owner', 'Analyst', 'Lead', 'Consultant', 'Coach']
                
                if any(kw in line for kw in job_keywords):
                    return line[:80]
        
        # Fallback: Filename
        if filename:
            return filename.replace('.pdf', '').replace('.docx', '').replace('_', ' ')[:80]
        
        return None
    
    def _extract_organization(self, text: str) -> Optional[str]:
        """
        Extrahiere Firmenname
        
        Patterns:
        - "bei FIRMA GmbH"
        - "Job bei FIRMA"
        - "FIRMA sucht"
        - Erste Zeile (oft Firma)
        """
        # Pattern 1: "bei FIRMA" oder "@ FIRMA"
        bei_pattern = r'(?:bei|@)\s+([A-ZÄÖÜ][^\n]{2,40})(?:\s+GmbH|\s+AG|\s+SE|\s+e\.V\.|\s+Inc|\s+Ltd)?'
        match = re.search(bei_pattern, text[:1000])
        if match:
            org = match.group(1).strip()
            # Säubere
            org = re.sub(r'\s+(?:GmbH|AG|SE|e\.V\.|Inc|Ltd).*$', '', org)
            org = org.strip()
            if 3 < len(org) < 50 and not any(kw in org.lower() for kw in ['job', 'stelle', 'karriere', 'bewerb']):
                return org
        
        # Pattern 2: GmbH/AG/SE Patterns
        for pattern in self.organization_patterns:
            match = re.search(pattern, text[:1000])
            if match:
                org = match.group(1).strip()
                if 3 < len(org) < 50:
                    return org
        
        # Pattern 3: "FIRMA sucht" oder "FIRMA stellt ein"
        sucht_pattern = r'([A-ZÄÖÜ][^\n]{2,40})\s+(?:sucht|stellt ein|hiring)'
        match = re.search(sucht_pattern, text[:500])
        if match:
            org = match.group(1).strip()
            if 3 < len(org) < 50 and not any(kw in org.lower() for kw in ['wir', 'unser', 'job']):
                return org
        
        # Pattern 4: Erste relevante Zeile (oft Logo/Firma)
        lines = text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            # Firmenname oft in erster Zeile, 5-50 Zeichen, beginnt mit Großbuchstabe
            if 5 < len(line) < 50 and line[0].isupper():
                # Skip typische Nicht-Firmen-Zeilen
                skip_words = ['job', 'stelle', 'karriere', 'bewerb', 'position', 'suchen', 'gesucht', 'vollzeit', 'teilzeit']
                if not any(kw in line.lower() for kw in skip_words):
                    # Kann Firma sein
                    return line
        
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extrahiere Standort"""
        text_upper = text[:2000]
        
        for city in self.location_keywords:
            if city in text_upper:
                return city
        
        return None
    
    def _extract_year(self, text: str, filename: Optional[str] = None) -> Optional[int]:
        """
        Extrahiere Jahr aus Text oder Filename
        
        Patterns:
        - 2024-10-27 (ISO)
        - 27.10.2024 (DE)
        - Oktober 2024
        - Stand: 2024
        - Copyright 2024
        - Filename mit Jahr
        """
        import datetime
        current_year = datetime.datetime.now().year
        
        # Pattern 1: ISO-Datum (2024-10-27)
        match = re.search(r'(20[12]\d)-\d{2}-\d{2}', text[:2000])
        if match:
            year = int(match.group(1))
            if 2018 <= year <= current_year:
                return year
        
        # Pattern 2: Deutsches Datum (27.10.2024)
        match = re.search(r'\d{1,2}\.\d{1,2}\.(20[12]\d)', text[:2000])
        if match:
            year = int(match.group(1))
            if 2018 <= year <= current_year:
                return year
        
        # Pattern 3: Monat Jahr (Oktober 2024, Oct 2024)
        month_pattern = r'(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[^\d]*(20[12]\d)'
        match = re.search(month_pattern, text[:2000], re.IGNORECASE)
        if match:
            year = int(match.group(1))
            if 2018 <= year <= current_year:
                return year
        
        # Pattern 4: "Stand: 2024", "Copyright 2024", "© 2024"
        match = re.search(r'(?:Stand|Copyright|©)[^\d]*(20[12]\d)', text[:2000], re.IGNORECASE)
        if match:
            year = int(match.group(1))
            if 2018 <= year <= current_year:
                return year
        
        # Pattern 5: Einfach "2024" im Text (letztes Vorkommen)
        years = re.findall(r'\b(20[12]\d)\b', text[:2000])
        if years:
            # Nimm das häufigste Jahr
            from collections import Counter
            year_counts = Counter(years)
            most_common_year = int(year_counts.most_common(1)[0][0])
            if 2018 <= most_common_year <= current_year:
                return most_common_year
        
        # Pattern 6: Aus Filename
        if filename:
            match = re.search(r'(20[12]\d)', filename)
            if match:
                year = int(match.group(1))
                if 2018 <= year <= current_year:
                    return year
        
        # Fallback: Aktuelles Jahr wenn gar nichts gefunden
        # (PDFs sind meist aktuell)
        return current_year
    
    def _check_remote(self, text: str) -> Optional[bool]:
        """Prüfe Remote-Option"""
        remote_keywords = ['remote', 'home office', 'homeoffice', 'hybrid']
        text_lower = text[:1000].lower()
        
        return any(kw in text_lower for kw in remote_keywords)
    
    def _extract_job_type(self, text: str) -> Optional[str]:
        """Extrahiere Job-Typ"""
        text_lower = text[:1000].lower()
        
        if 'vollzeit' in text_lower or 'full-time' in text_lower:
            return 'Vollzeit'
        elif 'teilzeit' in text_lower or 'part-time' in text_lower:
            return 'Teilzeit'
        elif 'werkstudent' in text_lower:
            return 'Werkstudent'
        elif 'praktikum' in text_lower or 'internship' in text_lower:
            return 'Praktikum'
        
        return None
    
    def _infer_job_category(self, text: str) -> Optional[str]:
        """Leite Berufsgruppe ab"""
        text_lower = text[:500].lower()
        
        if any(kw in text_lower for kw in ['ux', 'ui', 'user experience', 'user interface', 'design']):
            return 'UX/UI Design'
        elif any(kw in text_lower for kw in ['product owner', 'product manager', 'po', 'pm']):
            return 'Product Management'
        elif any(kw in text_lower for kw in ['agile coach', 'scrum master', 'rte']):
            return 'Agile Coaching'
        elif any(kw in text_lower for kw in ['frontend', 'react', 'vue', 'angular']):
            return 'Frontend Development'
        elif any(kw in text_lower for kw in ['backend', 'java', 'python', 'node']):
            return 'Backend Development'
        
        return 'Sonstige'  # Muss zum Enum-Wert passen!
    
    # =============================================================
    # STUFE 3: ERWEITERTE METADATEN
    # =============================================================
    
    def _extract_salary(self, text: str) -> tuple[Optional[int], Optional[int]]:
        """
        Extrahiere Gehaltsspanne
        
        Patterns:
        - 65.000 - 95.000 €
        - 50k-70k
        - bis zu 80.000€ p.a.
        - € 60.000-80.000
        
        Returns:
            (min, max) in Euro/Jahr
        """
        # Pattern 1: "65.000 - 95.000 €"
        pattern1 = r'([\d.]+)\s*[-–]\s*([\d.]+)\s*€'
        match = re.search(pattern1, text[:3000])
        if match:
            min_val = int(match.group(1).replace('.', ''))
            max_val = int(match.group(2).replace('.', ''))
            if 10000 <= min_val <= 200000 and 10000 <= max_val <= 200000:
                return (min_val, max_val)
        
        # Pattern 2: "50k-70k" oder "50K-70K"
        pattern2 = r'(\d+)[kK]\s*[-–]\s*(\d+)[kK]'
        match = re.search(pattern2, text[:3000])
        if match:
            min_val = int(match.group(1)) * 1000
            max_val = int(match.group(2)) * 1000
            return (min_val, max_val)
        
        # Pattern 3: "bis zu 80.000€"
        pattern3 = r'bis\s+zu\s+([\d.]+)\s*€'
        match = re.search(pattern3, text[:3000], re.IGNORECASE)
        if match:
            max_val = int(match.group(1).replace('.', ''))
            if 10000 <= max_val <= 200000:
                return (None, max_val)
        
        # Pattern 4: "€ 60.000-80.000" oder "€60k-80k"
        pattern4 = r'€\s*([\d.]+[kK]?)\s*[-–]\s*([\d.]+[kK]?)'
        match = re.search(pattern4, text[:3000])
        if match:
            min_str = match.group(1).replace('.', '')
            max_str = match.group(2).replace('.', '')
            
            min_val = int(min_str.replace('k', '').replace('K', ''))
            max_val = int(max_str.replace('k', '').replace('K', ''))
            
            if 'k' in min_str.lower():
                min_val *= 1000
            if 'k' in max_str.lower():
                max_val *= 1000
            
            if 10000 <= min_val <= 200000 and 10000 <= max_val <= 200000:
                return (min_val, max_val)
        
        return (None, None)
    
    def _extract_experience(self, text: str) -> tuple[Optional[int], Optional[int]]:
        """
        Extrahiere Erfahrungsjahre
        
        Patterns:
        - 3+ Jahre Erfahrung
        - mindestens 5 Jahre
        - 2-4 Jahre
        - mehrjährige Berufserfahrung
        
        Returns:
            (min, max) Jahre
        """
        # Pattern 1: "3+ Jahre"
        pattern1 = r'(\d+)\+\s*Jahre'
        match = re.search(pattern1, text[:3000], re.IGNORECASE)
        if match:
            years = int(match.group(1))
            return (years, None)
        
        # Pattern 2: "mindestens 5 Jahre"
        pattern2 = r'mindestens\s+(\d+)\s+Jahre'
        match = re.search(pattern2, text[:3000], re.IGNORECASE)
        if match:
            years = int(match.group(1))
            return (years, None)
        
        # Pattern 3: "2-4 Jahre"
        pattern3 = r'(\d+)\s*[-–]\s*(\d+)\s+Jahre'
        match = re.search(pattern3, text[:3000], re.IGNORECASE)
        if match:
            min_years = int(match.group(1))
            max_years = int(match.group(2))
            return (min_years, max_years)
        
        # Pattern 4: "mehrjährige Berufserfahrung"
        if re.search(r'mehrjährige|langjährige', text[:3000], re.IGNORECASE):
            return (3, None)  # Annahme: mehrjährig = 3+
        
        return (None, None)
    
    def _extract_education(self, text: str) -> Optional[str]:
        """
        Extrahiere Bildungsgrad
        
        Returns:
            "Bachelor", "Master", "PhD", "Ausbildung" oder None
        """
        text_lower = text[:3000].lower()
        
        # PhD/Doktor
        if any(kw in text_lower for kw in ['phd', 'doktor', 'promotion', 'dr.']):
            return 'PhD'
        
        # Master
        if any(kw in text_lower for kw in ['master', 'm.sc.', 'm.a.', 'm.eng.']):
            return 'Master'
        
        # Bachelor
        if any(kw in text_lower for kw in ['bachelor', 'b.sc.', 'b.a.', 'b.eng.']):
            return 'Bachelor'
        
        # Ausbildung
        if any(kw in text_lower for kw in ['ausbildung', 'berufsausbildung', 'lehre']):
            return 'Ausbildung'
        
        # Allgemein "abgeschlossenes Studium"
        if 'studium' in text_lower and 'abgeschlossen' in text_lower:
            return 'Bachelor'  # Minimum angenommen
        
        return None
    
    def _extract_languages(self, text: str) -> dict:
        """
        Extrahiere Sprachen mit Niveau
        
        Returns:
            {"Englisch": "C1", "Deutsch": "Muttersprache"}
        """
        languages = {}
        
        # Deutsch
        if re.search(r'\bDeutsch\b', text[:3000], re.IGNORECASE):
            if re.search(r'Muttersprache|native', text[:3000], re.IGNORECASE):
                languages['Deutsch'] = 'Muttersprache'
            elif re.search(r'fließend|fluent|verhandlungssicher', text[:3000], re.IGNORECASE):
                languages['Deutsch'] = 'Fließend'
            else:
                languages['Deutsch'] = 'Erforderlich'
        
        # Englisch
        if re.search(r'\bEnglisch\b|\bEnglish\b', text[:3000], re.IGNORECASE):
            # Niveau extrahieren
            niveau_match = re.search(r'Englisch[^\n]{0,50}(C[12]|B[12]|A[12])', text[:3000], re.IGNORECASE)
            if niveau_match:
                languages['Englisch'] = niveau_match.group(1).upper()
            elif re.search(r'fließend|fluent|verhandlungssicher', text[:3000], re.IGNORECASE):
                languages['Englisch'] = 'Fließend'
            else:
                languages['Englisch'] = 'Erforderlich'
        
        return languages
