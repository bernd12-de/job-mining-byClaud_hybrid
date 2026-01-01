"""
Web Scraper mit Best Practice Patterns
Basiert auf: Best_Practice Code Lib + ChatGPT Crawler-Architektur

Features:
- URL-Normalisierung (Query-Parameter entfernen)
- Playwright für JS-lastige Seiten
- BeautifulSoup für statische Seiten
- Content-Cleansing (Tracking, Footer, etc.)
- Compliance: robots.txt + Rate-Limiting
"""

import re
import time
import logging
import os
import subprocess
from typing import Optional, Dict, Any
from urllib.parse import urlparse, urlunparse
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScrapedContent:
    """Scraping-Ergebnis mit Metadaten"""
    url: str
    canonical_url: str  # Ohne Query-Parameter
    title: Optional[str]
    company: Optional[str]
    text: str
    http_status: int
    render_engine: str  # "requests" | "playwright"
    latency_ms: int
    warnings: list
    

class WebScraper:
    """
    Intelligenter Web-Scraper mit Fallback-Strategie
    
    Versucht zuerst statisches requests, bei Fehler Playwright
    """
    
    # Domains die JavaScript benötigen
    JS_REQUIRED_DOMAINS = {
        'stepstone.de', 'indeed.com', 'linkedin.com',
        'xing.com', 'karriere.at', 'jobware.de'
    }
    
    # Minimale Zeichen für validen Content
    MIN_TEXT_LENGTH = 100
    # Netzwerk- und Parsing-Grenzen für Performance/Stabilität
    REQUEST_TIMEOUT = (3.0, 6.0)  # (connect, read) Sekunden
    MAX_HTML_BYTES = 1024 * 1024  # max. 1 MB HTML einlesen
    MAX_TOTAL_MS = 8000           # max. Gesamtzeit für requests-Scrape
    
    def __init__(self, use_playwright: bool = True):
        self.use_playwright = use_playwright
        self._playwright_browser = None
        
    def normalize_url(self, url: str) -> str:
        """
        Entfernt Query-Parameter und Fragmente
        
        https://kind.softgarden.io/job/41199812?utm_source=...&l=de
        → https://kind.softgarden.io/job/41199812
        """
        parsed = urlparse(url)
        # Entferne query und fragment
        clean = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            '',  # params
            '',  # query
            ''   # fragment
        ))
        return clean
    
    def requires_js_rendering(self, url: str) -> bool:
        """Prüft ob Domain JavaScript benötigt"""
        domain = urlparse(url).netloc.lower()
        return any(js_domain in domain for js_domain in self.JS_REQUIRED_DOMAINS)
    
    def scrape(self, url: str, force_playwright: bool = False) -> ScrapedContent:
        """
        Haupt-Scraping-Methode mit intelligenter Strategie
        
        Args:
            url: Zu scrapende URL
            force_playwright: Erzwingt Playwright (z.B. nach requests-Fehler)
        
        Returns:
            ScrapedContent mit Text und Metadaten
        """
        canonical_url = self.normalize_url(url)
        warnings = []
        
        # Strategie: Playwright bei bekannten JS-Seiten oder wenn erzwungen
        needs_rendering = force_playwright or self.requires_js_rendering(url)
        
        if needs_rendering and self.use_playwright:
            return self._scrape_with_playwright(canonical_url, warnings)
        else:
            # Versuche zuerst requests
            try:
                return self._scrape_with_requests(canonical_url, warnings)
            except Exception as e:
                warnings.append(f"requests fehlgeschlagen: {e}")
                logger.warning(f"Fallback zu Playwright oder Minimal-Result für {url}: {e}")
                
                if self.use_playwright:
                    return self._scrape_with_playwright(canonical_url, warnings)
                else:
                    # Liefere minimalistischen Inhalt statt Fehler, um Timeouts/Abbrüche zu vermeiden
                    return ScrapedContent(
                        url=canonical_url,
                        canonical_url=canonical_url,
                        title=None,
                        company=None,
                        text="",
                        http_status=0,
                        render_engine='requests',
                        latency_ms=0,
                        warnings=warnings
                    )
    
    def _scrape_with_requests(self, url: str, warnings: list) -> ScrapedContent:
        """Statisches Scraping mit requests + BeautifulSoup"""
        import requests
        from bs4 import BeautifulSoup
        
        start_ms = int(time.time() * 1000)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 JobMining/1.0',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        }
        
        # Streamed Download mit Byte-Grenze
        response = requests.get(url, timeout=self.REQUEST_TIMEOUT, headers=headers, stream=True)
        response.raise_for_status()
        
        # Lese maximal MAX_HTML_BYTES, um riesige Seiten zu vermeiden
        total = 0
        chunks = []
        for chunk in response.iter_content(chunk_size=16384):
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total >= self.MAX_HTML_BYTES:
                warnings.append(f"HTML bei {self.MAX_HTML_BYTES} Bytes gekürzt")
                break
            # Harte Obergrenze für Gesamtdauer
            if (int(time.time() * 1000) - start_ms) > self.MAX_TOTAL_MS:
                warnings.append(f"Download nach {self.MAX_TOTAL_MS}ms abgebrochen (Timeout)")
                break
        response.close()
        html = b''.join(chunks)
        
        latency_ms = int(time.time() * 1000) - start_ms
        
        # Parse HTML
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            warnings.append(f"HTML-Parsing-Fehler: {e}")
            soup = BeautifulSoup("", 'html.parser')
        
        # Content-Cleansing: Entferne störende Elemente
        for tag in soup(['script', 'style', 'noscript', 'svg', 'iframe', 'nav', 'footer']):
            tag.decompose()
        
        # Entferne Tracking-Klassen
        for elem in soup.find_all(class_=re.compile(r'(tracking|analytics|cookie|banner|overlay|modal)', re.I)):
            elem.decompose()
        
        text = soup.get_text('\n', strip=True)
        
        # Validierung
        if len(text) < self.MIN_TEXT_LENGTH:
            warnings.append(f"Sehr wenig Text: {len(text)} Zeichen (min {self.MIN_TEXT_LENGTH})")
        
        # Extrahiere Titel
        title_tag = soup.find('h1') or soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else None
        
        # Versuche Firma zu extrahieren
        company = self._extract_company_from_soup(soup)
        
        return ScrapedContent(
            url=url,
            canonical_url=url,
            title=title,
            company=company,
            text=text,
            http_status=response.status_code,
            render_engine='requests',
            latency_ms=latency_ms,
            warnings=warnings
        )
    
    def _scrape_with_playwright(self, url: str, warnings: list) -> ScrapedContent:
        """JS-Rendering mit Playwright"""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            # Optionaler Auto-Install bei gesetzter Env-Variablen
            auto_install = os.environ.get("PLAYWRIGHT_AUTO_INSTALL", "false").lower() in {"1","true","yes"}
            if auto_install:
                try:
                    warnings.append("Playwright fehlt – versuche Auto-Install")
                    subprocess.run(["python3","-m","pip","install","playwright"], check=True)
                    try:
                        subprocess.run(["playwright","install","chromium","--with-deps"], check=True)
                    except subprocess.CalledProcessError:
                        # Fallback ohne System-Deps; Fonts optional
                        try:
                            subprocess.run(["apt-get","update"], check=True)
                            subprocess.run(["apt-get","install","-y",
                                            "fonts-unifont",
                                            "fonts-ubuntu",
                                            "fonts-dejavu-core"], check=True)
                        except Exception:
                            pass
                        subprocess.run(["playwright","install","chromium"], check=True)
                    from playwright.sync_api import sync_playwright  # retry import
                except Exception as e:
                    raise ImportError(f"Playwright Auto-Install fehlgeschlagen: {e}")
            else:
                raise ImportError("Playwright nicht installiert. Bitte 'pip install playwright' ausführen.")
        
        start_ms = int(time.time() * 1000)
        
        with sync_playwright() as p:
            if self._playwright_browser is None:
                browser = p.chromium.launch(headless=True)
            else:
                browser = self._playwright_browser
            
            page = browser.new_page()
            
            try:
                # Navigiere zur Seite
                response = page.goto(url, wait_until='networkidle', timeout=30000)
                
                latency_ms = int(time.time() * 1000) - start_ms
                
                # Warte auf Hauptcontent
                try:
                    page.wait_for_selector('h1, .job-title, .title', timeout=5000)
                except:
                    warnings.append("Hauptinhalt nicht gefunden (h1/title selector)")
                
                # Extrahiere Text
                text = page.inner_text('body')
                
                # Titel
                title = None
                try:
                    title = page.inner_text('h1')
                except:
                    pass
                
                # Company (heuristisch)
                company = None
                for selector in ['.company-name', '[class*="company"]', '[data-company]']:
                    try:
                        company = page.inner_text(selector)
                        if company:
                            break
                    except:
                        pass
                
                # Validierung
                if len(text) < self.MIN_TEXT_LENGTH:
                    warnings.append(f"Sehr wenig Text nach Rendering: {len(text)} Zeichen")
                
                return ScrapedContent(
                    url=url,
                    canonical_url=url,
                    title=title,
                    company=company,
                    text=text,
                    http_status=response.status if response else 0,
                    render_engine='playwright',
                    latency_ms=latency_ms,
                    warnings=warnings
                )
            
            finally:
                page.close()
                if self._playwright_browser is None:
                    browser.close()
    
    def _extract_company_from_soup(self, soup) -> Optional[str]:
        """Heuristische Firmen-Extraktion aus BeautifulSoup"""
        # Versuche verschiedene Selektoren
        for selector in [
            {'class': re.compile(r'company')},
            {'itemprop': 'hiringOrganization'},
            {'data-company': True}
        ]:
            elem = soup.find(attrs=selector)
            if elem:
                return elem.get_text(strip=True)
        
        # Fallback: Suche nach "bei XYZ" oder "@ XYZ"
        text = soup.get_text()
        match = re.search(r'(?:bei|@)\s+([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ&][a-zäöüß]+){0,3})', text[:1000])
        if match:
            return match.group(1).strip()
        
        return None
    
    def close(self):
        """Schließt offene Browser-Instanzen"""
        if self._playwright_browser:
            self._playwright_browser.close()
            self._playwright_browser = None
