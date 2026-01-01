import logging
from typing import BinaryIO, Optional

# Core & Domain
from app.core.normalize import parse_date
from app.domain.models import AnalysisResultDTO

# Interfaces
from app.interfaces.interfaces import (
    IJobMiningWorkflowManager,
    ITextExtractor,
    ICompetenceExtractor
)

# Services & Factory
from app.application.factories.analysis_result_factory import AnalysisResultFactory
from app.infrastructure.extractor.metadata_extractor import MetadataExtractor
from app.infrastructure.extractor.discovery_logger import log_candidates

logger = logging.getLogger(__name__)

class JobMiningWorkflowManager(IJobMiningWorkflowManager):
    """
    Der Manager ist nur noch der Orchestrator für EINE Datei.
    Er weiß nichts von Ordnern (Batch) oder HTTP-Requests.
    """

    def __init__(self,
                 text_extractor: ITextExtractor,
                 competence_extractor: ICompetenceExtractor,
                 organization_service,
                 role_service,
                 metadata_extractor: MetadataExtractor):

        self.text_extractor = text_extractor
        self.competence_extractor = competence_extractor
        self.organization_service = organization_service
        self.role_service = role_service
        self.metadata_extractor = metadata_extractor

    async def run_full_analysis(self, file_object: BinaryIO, filename: str) -> AnalysisResultDTO:
        """
        Einstiegspunkt 1: Dateibasierte Analyse (PDF, DOCX via Upload oder Batch).
        Wird von api_endpoints.py (Upload) UND JobDirectoryProcessor (Batch) genutzt.
        Mit umfassender Fehlerbehandlung.
        """
        try:
            # 1. Text extrahieren (Delegation an AdvancedTextExtractor)
            text = self.text_extractor.extract_text(file_object, filename)

            if not text:
                # Fehler werfen oder leeres Result zurückgeben (hier: Fehler für sauberes Logging)
                logger.error(f"AdvancedTextExtractor lieferte leeren Text für '{filename}'.")
                raise ValueError(f"AdvancedTextExtractor konnte keinen Text aus {filename} lesen.")

            # 2. Cleaning (WICHTIG: Null-Bytes entfernen, sonst DB-Fehler oder 'kein Text')
            cleaned_raw_text = text.replace('\x00', '')

            return self._execute_pipeline(cleaned_raw_text, source_name=filename)
        except ValueError as e:
            # Validierungsfehler weiterwerfen
            raise
        except Exception as e:
            logger.error(f"❌ Fehler bei run_full_analysis für '{filename}': {e}", exc_info=True)
            raise ValueError(f"Analyse-Fehler für {filename}: {str(e)}")

    def run_analysis_from_scraped_text(self, text: str, source_name: str) -> AnalysisResultDTO:
        """
        Einstiegspunkt 2: Textbasierte Analyse (Web Scraper).
        Mit Fehlerbehandlung.
        """
        try:
            # Auch hier Cleaning sicherheitshalber
            cleaned_text = text.replace('\x00', '')
            return self._execute_pipeline(cleaned_text, source_name=source_name, source_url=source_name if source_name.startswith('http') else None)
        except Exception as e:
            logger.error(f"❌ Fehler bei run_analysis_from_scraped_text für '{source_name}': {e}", exc_info=True)
            raise ValueError(f"Analyse-Fehler für {source_name}: {str(e)}")

    # Kompatibilitäts-Alias: Einige Tests/Clients nutzen noch die interne Methode `_run_analysis_from_text`
    def _run_analysis_from_text(self, text: str, source_name: str) -> AnalysisResultDTO:
        return self.run_analysis_from_scraped_text(text, source_name)

    def _execute_pipeline(self, text: str, source_name: str, source_url: Optional[str] = None) -> AnalysisResultDTO:
        """
        Die KERN-LOGIK (SSoT).
        Hier läuft der CRISP-DM Prozess für ein einzelnes Dokument durch.
        Mit robuster Fehlerbehandlung an kritischen Stellen.
        """
        try:
            # ═══════════════════════════════════════
            # 📊 BEST PRACTICE: Detailliertes Status-Logging
            # ═══════════════════════════════════════
            logger.info("=" * 60)
            logger.info(f"🚀 ANALYSE START: {source_name}")
            logger.info("=" * 60)

            # Schritt A: Metadaten & Datum (Ebene 6)
            logger.info("--- 🏢 METADATA EXTRACTION")
            meta = {}
            try:
                meta = self.metadata_extractor.extract_all(text, filename=source_name)

                # ✅ BEST PRACTICE: Zeige extrahierte Metadaten
                logger.info(f"    ✓ Titel: \"{meta.get('job_title', 'N/A')}\"")
                logger.info(f"    ✓ Firma: \"{meta.get('company_name', 'N/A')}\"")
                logger.info(f"    ✓ Branch: {meta.get('industry', 'N/A')}")
                logger.info(f"    ✓ Ort: {meta.get('region', 'N/A')}")
                logger.info(f"    ✓ Datum: {meta.get('posting_date', 'N/A')}")
                logger.info(f"    ✓ Kategorie: {meta.get('job_role', 'N/A')}")

            except Exception as e:
                logger.warning(f"    ⚠️ Metadaten-Extraktion fehlgeschlagen: {e}")
                meta = {'job_title': 'Unbekannte Position', 'posting_date': '2024-12-01'}

            # --- 💎 GOLD: Smarte Segmentierung integriert ---
            tasks = meta.get('tasks_clean', '')
            reqs = meta.get('requirements_clean', '')
            # Baue "Konzentrat" für die KI
            segmented_text = (tasks + " " + reqs).strip()

            # Vorsegmentierter Text ohne Benefits/About-Blöcke
            prefiltered_text = meta.get('processing_text') or text

            # Fallback-Logik: Wenn Segmentierung fehlschlägt (z.B. < 50 Zeichen), nimm prefilter.
            if len(segmented_text) < 50:
                logger.info(f"Segmentierung für '{source_name}' zu kurz. Nutze vorgefilterten Text.")
                analysis_text = prefiltered_text if prefiltered_text else text
            else:
                analysis_text = segmented_text
            # -----------------------------------------------

            # Datum normalisieren (Fallback auf heute, falls MetadataExtractor nichts findet)
            posting_date = meta.get('posting_date') or "2024-12-01"

            # Schritt B: Kontext-Erkennung (Branche & Rolle)
            industry = None
            role = None
            
            try:
                # Versuche zuerst die neuere detect_industry API, fallback auf classify_industry (Legacy) falls nötig
                if hasattr(self.organization_service, 'detect_industry'):
                    industry = self.organization_service.detect_industry(text)
                
                if not isinstance(industry, str):
                    # Fallback
                    industry = getattr(self.organization_service, 'classify_industry', lambda t: None)(text)
            except Exception as e:
                logger.warning(f"⚠️ Industry-Erkennung fehlgeschlagen: {e}")
                industry = "Unbekannt"

            try:
                role = self.role_service.classify_role(text, meta.get('job_title') or source_name)
            except Exception as e:
                logger.warning(f"⚠️ Rollen-Erkennung fehlgeschlagen: {e}")
                role = "Unbekannt"

            # Schritt C: NLP Extraktion (Ebene 1-5)
            logger.info("")
            logger.info("--- 🔍 COMPETENCE EXTRACTION")
            competences = []
            try:
                # WICHTIG: Übergibt 'role' an den Extractor, wie im Interface gefixt.
                competences = self.competence_extractor.extract_competences(text=analysis_text, role=role)

                # ✅ BEST PRACTICE: Zeige Extraction-Ergebnis
                logger.info(f"    ✅ Extrahiert: {len(competences)} Kompetenzen")

                # Gruppiere nach Level
                level_counts = {}
                digital_count = 0
                discovery_count = 0
                for comp in competences:
                    level = getattr(comp, 'level', 2)
                    level_counts[level] = level_counts.get(level, 0) + 1
                    if getattr(comp, 'is_digital', False):
                        digital_count += 1
                    if getattr(comp, 'is_discovery', False):
                        discovery_count += 1

                logger.info(f"    📊 Breakdown:")
                for lvl in sorted(level_counts.keys()):
                    logger.info(f"       Level {lvl}: {level_counts[lvl]} Skills")
                if digital_count > 0:
                    logger.info(f"       Digital Skills: {digital_count}")
                if discovery_count > 0:
                    logger.info(f"       Discovery: {discovery_count}")

            except Exception as e:
                logger.error(f"    ❌ Kompetenz-Extraktion fehlgeschlagen: {e}", exc_info=True)
                # Weiter mit leerer Liste

            # Discovery: unbekannte Kandidaten sammeln (vereinfachte Heuristik)
            try:
                # Labels für Ausschluss (bekannte ESCO-Begriffe)
                known_labels = set()
                repo = getattr(self.competence_extractor, 'repository', None)
                if repo is not None and hasattr(repo, 'get_all_identifiable_labels'):
                    known_labels = set(l.lower() for l in (repo.get_all_identifiable_labels() or []))

                # Tokenisierung: einfache Wort-Tokens
                import re
                tokens = re.findall(r"[A-Za-zÄÖÜäöüß][-A-Za-z0-9ÄÖÜäöüß]{2,}", analysis_text)
                freq = {}
                for t in tokens:
                    tl = t.lower()
                    # Filter: nicht bereits bekannte Labels (roh oder kompakt), nicht zu kurz
                    if len(tl) < 4:
                        continue
                    if tl in known_labels or tl.replace(' ', '') in known_labels:
                        continue
                    # Ein paar triviale Stopwörter ausschließen
                    if tl in {"und", "oder", "die", "der", "das", "ein", "eine"}:
                        continue
                    freq[tl] = freq.get(tl, 0) + 1

                # Kandidaten nach Häufigkeit sortieren, Top-N
                top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:20]
                candidates = [{"term": k, "role": role, "context": "segmented", "count": v} for k, v in top]
                if candidates:
                    log_candidates(candidates)
            except Exception as e:
                # Discovery ist best-effort, Fehler hier sollen die Pipeline nicht stoppen
                logger.debug(f"Discovery-Logging fehlgeschlagen: {e}")
                pass

            # Schritt D: DTO Bauen (Ebene 7)
            try:
                # Nutzt die Factory, um Zirkelbezüge zu vermeiden.
                result = AnalysisResultFactory.create_result(
                    title=meta.get('job_title') or 'Unbekannte Position',
                    job_role=role,
                    industry=industry,
                    region=meta.get('region', "Unbekannt"),
                    posting_date=posting_date,
                    raw_text=text,
                    is_segmented=meta.get('is_segmented', False),
                    source_url=source_url,
                    competences=competences
                )

                # ✅ BEST PRACTICE: Final Summary
                logger.info("")
                logger.info("--- 📊 RESULT")
                logger.info(f"    ✅ Job: \"{meta.get('job_title', 'N/A')}\"")
                logger.info(f"    ✅ Firma: {meta.get('company_name', 'N/A')} ({industry})")
                logger.info(f"    ✅ Kompetenzen: {len(competences)} gesamt")
                logger.info("=" * 60)

                return result

            except Exception as e:
                logger.error(f"    ❌ DTO-Erstellung fehlgeschlagen: {e}", exc_info=True)
                raise ValueError(f"Konnte kein Analyse-Ergebnis erstellen: {str(e)}")
                
        except ValueError:
            # ValueError weiterwerfen (z.B. von DTO-Erstellung)
            raise
        except Exception as e:
            logger.error(f"❌ Kritischer Fehler in _execute_pipeline für '{source_name}': {e}", exc_info=True)
            raise ValueError(f"Pipeline-Fehler: {str(e)}")

    def create_competence_dto(self, **kwargs):
        """Zentrale Factory-Methode für Extractors (z.B. Discovery).
        Prüft Blacklist und Validität bevor ein CompetenceDTO erzeugt wird.
        Gibt None zurück, wenn das DTO verworfen werden soll.
        """
        term = kwargs.get('original_term', '')
        try:
            # Versuche die Blacklist über das Repository zu prüfen, falls vorhanden
            repo = getattr(self.competence_extractor, 'repository', None)
            if repo is not None and hasattr(repo, 'is_blacklisted') and repo.is_blacklisted(term):
                return None
        except Exception:
            pass

        try:
            return AnalysisResultFactory.create_competence(
                original_term=kwargs.get('original_term'),
                esco_label=kwargs.get('esco_label'),
                esco_uri=kwargs.get('esco_uri'),
                level=kwargs.get('level', 1),
                esco_group_code=kwargs.get('esco_group_code'),
                is_digital=kwargs.get('is_digital', False),
                is_discovery=kwargs.get('is_discovery', False),
                role_context=kwargs.get('role_context'),
                confidence=kwargs.get('confidence_score', 0.7)
            )
        except Exception:
            return None
