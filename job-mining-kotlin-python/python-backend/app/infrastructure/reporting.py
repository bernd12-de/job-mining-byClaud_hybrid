import json
import os
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any
from pathlib import Path
import io
import csv

from app.infrastructure.job_classifier import (
    classify_job_role,
    categorize_competence,
    group_jobs_by_category,
    group_skills_by_category,
)

BATCH_RESULTS_DIR = Path(os.getenv('BATCH_RESULTS_DIR', 'data/exports/batch_results'))


def _iter_job_files() -> List[Path]:
    if not BATCH_RESULTS_DIR.exists():
        return []
    return [p for p in BATCH_RESULTS_DIR.iterdir() if p.suffix.lower() == '.json' and p.name != 'summary.json']


def load_summary() -> Dict[str, Any]:
    summary_path = BATCH_RESULTS_DIR / 'summary.json'
    if not summary_path.exists():
        return {}
    with open(summary_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _should_include_in_top_skills(collections: List[str]) -> bool:
    """
    Filtert Skills nach ESCO-Collections:
    - ✅ Digital, Research → Wertvolle, spezifische Skills
    - ❌ Language, Transversal → Generic, zu breit für Top-Skills
    """
    if not collections:
        return True  # Occupation-specific Skills ohne Collection → behalten
    
    # Exclude wenn NUR Language oder Transversal
    if set(collections).issubset({'language', 'transversal'}):
        return False
    
    return True


def aggregate_top_skills(top_n: int = 10) -> List[Tuple[str, int]]:
    """Aggregiert Top Skills, filtert nach ESCO-Collections (keine Sprachen/Generic)."""
    counter = Counter()
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            for c in data.get('competences', []):
                label = c.get('esco_label') or c.get('original_term')
                collections = c.get('collections', [])
                
                if label and _should_include_in_top_skills(collections):
                    counter[label] += 1
        except Exception:
            continue
    return counter.most_common(top_n)


def aggregate_domain_mix() -> Dict[str, int]:
    """
    Aggregiert Domains basierend auf Job-Klassifizierung.
    Gruppiert in: Software Dev, Data Science, Product Management, UX/UI, Consulting, etc.
    """
    counter = Counter()
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            title = data.get('title', '')
            role = data.get('job_role', '')
            industry = data.get('industry', '')
            
            # Nutze die neue Job-Klassifizierung
            classification = classify_job_role(title, role, industry)
            category = classification['category']
            sub_category = classification['sub_category']
            
            # Kombiniere Haupt- und Unterkategorie
            if sub_category and sub_category != 'general':
                domain = f"{category.replace('_', ' ').title()} — {sub_category.replace('_', ' ').title()}"
            else:
                domain = category.replace('_', ' ').title()
            
            counter[domain] += 1
        except Exception:
            continue
    return dict(counter)


def aggregate_collection_breakdown() -> Dict[str, int]:
    """
    Zählt Skills nach Kompetenz-Kategorien (eigenes Modell + ESCO):
    - technical_core: Python, Java, Kotlin, C#, etc.
    - frameworks_tools: Spring, Django, FastAPI, React, etc.
    - data_ml: Pandas, NumPy, TensorFlow, NLP, etc.
    - design_ux: Figma, Adobe, Prototyping, UX Research, etc.
    - product_management: Scrum, Jira, Agile, Strategy, etc.
    - soft_skills: Kommunikation, Teamfähigkeit, Leadership, etc.
    - infrastructure: Docker, Kubernetes, AWS, Azure, etc.
    - database: SQL, PostgreSQL, MongoDB, etc.
    - languages: Deutsch, Englisch, etc.
    """
    counter = Counter()
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            for c in data.get('competences', []):
                label = c.get('esco_label') or c.get('original_term')
                collections = c.get('collections', [])
                
                if not label:
                    continue
                
                # Nutze die neue Kompetenz-Kategorisierung
                categorization = categorize_competence(label, collections)
                category = categorization['category']
                
                # Humanize category names
                category_display = category.replace('_', ' ').title()
                counter[category_display] += 1
        except Exception:
            continue
    return dict(counter)


def aggregate_time_series_for_skills(skills: List[str]) -> Dict[str, Dict[str, int]]:
    # return {skill: {year: count}}
    result = {s: defaultdict(int) for s in skills}
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            date = data.get('posting_date')
            if not date:
                continue
            year = date.split('-')[0]
            for c in data.get('competences', []):
                label = c.get('esco_label') or c.get('original_term')
                if label in result:
                    result[label][year] += 1
        except Exception:
            continue
    # convert defaultdicts to dicts
    return {skill: dict(year_counts) for skill, year_counts in result.items()}


def generate_csv_report() -> io.BytesIO:
    # produce a simple CSV with one row per job and flattened competence labels
    rows = []
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            competences = [c.get('esco_label') or c.get('original_term') for c in data.get('competences', [])]
            rows.append({
                'title': data.get('title'),
                'job_role': data.get('job_role'),
                'region': data.get('region'),
                'industry': data.get('industry'),
                'posting_date': data.get('posting_date'),
                'skills_count': len(competences),
                'skills': '|'.join(competences)
            })
        except Exception:
            continue

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['title', 'job_role', 'region', 'industry', 'posting_date', 'skills_count', 'skills'], delimiter=',')
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

    bio = io.BytesIO()
    bio.write(output.getvalue().encode('utf-8'))
    bio.seek(0)
    return bio


def generate_pdf_report() -> io.BytesIO:
    """Generiert einen einfachen PDF-Report mit den Dashboard-Metriken (minimal, für Prototyp)."""
    metrics = build_dashboard_metrics(top_n=10)

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception as e:
        # Wenn reportlab nicht verfügbar ist, raise klaren Fehler
        raise RuntimeError("reportlab ist nicht installiert. Bitte 'reportlab' in requirements.txt hinzufügen.")

    bio = io.BytesIO()
    c = canvas.Canvas(bio, pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "Job Mining — Report")
    c.setFont("Helvetica", 10)
    c.drawString(50, 780, f"Total Jobs: {metrics.get('total_jobs', 0)}")
    c.drawString(50, 765, f"Total Skills: {metrics.get('total_skills', 0)}")

    y = 740
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Top Skills:")
    y -= 18
    c.setFont("Helvetica", 10)
    for s in metrics.get('top_skills', []):
        c.drawString(60, y, f"{s.get('skill')}: {s.get('count')}")
        y -= 14
        if y < 60:
            c.showPage()
            y = 800
    c.showPage()
    c.save()
    bio.seek(0)
    return bio


def aggregate_digital_skills_count() -> int:
    """Zählt digitale Skills basierend auf ESCO 'is_digital' Flag."""
    digital_count = 0
    seen_skills = set()

    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            for c in data.get('competences', []):
                label = c.get('esco_label') or c.get('original_term')
                is_digital = c.get('is_digital', False)

                if label and is_digital and label not in seen_skills:
                    seen_skills.add(label)
                    digital_count += 1
        except Exception:
            continue

    return digital_count


def aggregate_regional_distribution() -> Dict[str, int]:
    """Aggregiert Jobs nach Region/Stadt."""
    counter = Counter()

    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            region = data.get('region', 'Unbekannt')
            if region:
                counter[region] += 1
        except Exception:
            continue

    return dict(counter)


def aggregate_emerging_skills(min_year: int = 2024) -> List[Dict[str, Any]]:
    """
    Identifiziert aufstrebende Skills durch Wachstumsanalyse.
    Vergleicht aktuelle Jahre (>=min_year) mit Vorjahren.
    """
    skill_by_year = defaultdict(lambda: defaultdict(int))

    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            date = data.get('posting_date')
            if not date:
                continue

            year = int(date.split('-')[0])

            for c in data.get('competences', []):
                label = c.get('esco_label') or c.get('original_term')
                collections = c.get('collections', [])

                if label and _should_include_in_top_skills(collections):
                    skill_by_year[label][year] += 1
        except Exception:
            continue

    # Berechne Wachstum
    growth_data = []
    for skill, year_counts in skill_by_year.items():
        recent = sum(count for year, count in year_counts.items() if year >= min_year)
        older = sum(count for year, count in year_counts.items() if year < min_year)

        if recent > 0 and older > 0:
            growth = recent - older
            growth_pct = ((recent - older) / older) * 100 if older > 0 else 0

            growth_data.append({
                'skill': skill,
                'growth': growth,
                'growth_pct': round(growth_pct, 1),
                'recent_count': recent,
                'older_count': older
            })
        elif recent > 5:  # Neue Skills ohne Historie
            growth_data.append({
                'skill': skill,
                'growth': recent,
                'growth_pct': 999,  # Marker für "NEU"
                'recent_count': recent,
                'older_count': 0
            })

    # Sortiere nach Wachstum
    growth_data.sort(key=lambda x: x['growth'], reverse=True)
    return growth_data[:10]


def aggregate_quality_metrics() -> Dict[str, Any]:
    """
    Aggregiert Qualitätsmetriken der Extraktion.
    Kategorisiert Jobs nach Extraktionsqualität.
    """
    quality_buckets = {
        'excellent': 0,  # >= 90%
        'good': 0,       # 70-89%
        'fair': 0,       # 50-69%
        'poor': 0        # < 50%
    }

    extraction_rates = []

    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            total_comps = len(data.get('competences', []))

            if total_comps == 0:
                quality_buckets['poor'] += 1
                extraction_rates.append(0)
                continue

            # Schätze Qualität basierend auf Anzahl extrahierter Kompetenzen
            # (20-50 ist optimal laut Anforderungen)
            if 20 <= total_comps <= 50:
                quality_pct = 90 + (40 - abs(total_comps - 35)) / 15 * 10  # Peak bei 35
            elif total_comps < 20:
                quality_pct = max(50, (total_comps / 20) * 90)
            else:
                quality_pct = max(50, 90 - ((total_comps - 50) / 50) * 20)

            quality_pct = min(100, max(0, quality_pct))
            extraction_rates.append(quality_pct)

            if quality_pct >= 90:
                quality_buckets['excellent'] += 1
            elif quality_pct >= 70:
                quality_buckets['good'] += 1
            elif quality_pct >= 50:
                quality_buckets['fair'] += 1
            else:
                quality_buckets['poor'] += 1
        except Exception:
            continue

    avg_quality = sum(extraction_rates) / len(extraction_rates) if extraction_rates else 0

    return {
        'buckets': quality_buckets,
        'avg_quality': round(avg_quality, 1),
        'total_analyzed': len(extraction_rates)
    }


def aggregate_level_progression() -> Dict[str, int]:
    """
    Aggregiert Skills nach 7-Ebenen-Modell (gemäß Dokumentation 7_ebenen_summary.md).

    Ebene 1: Discovery (neue unbekannte Begriffe mit is_discovery=True)
    Ebene 2: ESCO/SSoT (standardisierte Skills aus ESCO)
    Ebene 3: Digital (digitale Skills mit is_digital=True)
    Ebene 4: Fachbücher (aus Fachbuch-PDFs extrahiert)
    Ebene 5: Academia (aus Modulhandbüchern extrahiert)
    Ebene 6: Segmentierung & Kontext (Analyse-Ebene, nicht in Kompetenzen)
    Ebene 7: Zeitreihen/Validierung (Analyse-Ebene, nicht in Kompetenzen)
    """
    # Korrekte Level-Namen gemäß 7_ebenen_summary.md
    level_counts = {
        'Level 1 (Discovery)': 0,
        'Level 2 (ESCO/SSoT)': 0,
        'Level 3 (Digital)': 0,
        'Level 4 (Fachbücher)': 0,
        'Level 5 (Academia)': 0,
        'Level 6 (Segmentierung)': 0,
        'Level 7 (Zeitreihen)': 0,
    }

    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            for c in data.get('competences', []):
                # Nutze direkt das 'level' Feld aus den Competence-Daten
                level = c.get('level', 2)  # Default: Level 2 (ESCO)
                is_discovery = c.get('is_discovery', False)
                is_digital = c.get('is_digital', False)

                # Level-Zuordnung basierend auf tatsächlichen Daten
                if is_discovery or level == 1:
                    level_counts['Level 1 (Discovery)'] += 1
                elif level == 5:
                    level_counts['Level 5 (Academia)'] += 1
                elif level == 4:
                    level_counts['Level 4 (Fachbücher)'] += 1
                elif is_digital or level == 3:
                    level_counts['Level 3 (Digital)'] += 1
                elif level == 2:
                    level_counts['Level 2 (ESCO/SSoT)'] += 1
                else:
                    # Fallback für unbekannte Levels
                    level_counts['Level 2 (ESCO/SSoT)'] += 1

                # Level 6 & 7 sind Analyse-Ebenen, nicht in einzelnen Kompetenzen
                # Diese werden nicht aus Job-Daten gezählt
        except Exception:
            continue

    return level_counts


def aggregate_pipeline_metrics() -> Dict[str, float]:
    """
    Berechnet Pipeline-Qualitätsmetriken.
    Placeholder - in echtem System würde man aus Logs/Metriken lesen.
    """
    return {
        'segmentierung_erfolg': 92.0,
        'fuzzy_match_praezision': 94.0,
        'extraktionsqualitaet': 87.0,
        'pipeline_gesundheit': 89.0,
    }


def aggregate_time_series_validation() -> Dict[str, Any]:
    """
    Validiert Zeitreihen-Daten (Level 7: Zeitreihen/Validierung).

    Prüft:
    - Ausreichend Datenpunkte für Trend-Analyse
    - Lücken in Zeitreihen
    - Datenqualität über Zeit
    - Trend-Klassifikation (Rising/Stable/Falling)
    """
    skill_by_year = defaultdict(lambda: defaultdict(int))

    # Sammle alle Zeitreihen-Daten
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            date = data.get('posting_date')
            if not date:
                continue

            year = int(date.split('-')[0])

            for c in data.get('competences', []):
                label = c.get('esco_label') or c.get('original_term')
                collections = c.get('collections', [])

                if label and _should_include_in_top_skills(collections):
                    skill_by_year[label][year] += 1
        except Exception:
            continue

    # Validierungs-Metriken
    validated_skills = 0
    skills_with_gaps = 0
    skills_with_trend = 0
    total_skills = len(skill_by_year)

    min_years = 3  # Mindestens 3 Jahre für valide Zeitreihe

    rising_trends = 0
    falling_trends = 0
    stable_trends = 0

    for skill, year_counts in skill_by_year.items():
        years = sorted(year_counts.keys())

        # Prüfung 1: Genug Datenpunkte?
        if len(years) >= min_years:
            validated_skills += 1

            # Prüfung 2: Lücken in Zeitreihe?
            if len(years) > 1:
                year_range = range(min(years), max(years) + 1)
                if len(years) < len(list(year_range)):
                    skills_with_gaps += 1

            # Prüfung 3: Trend-Klassifikation
            # Vergleiche erste Hälfte mit zweiter Hälfte
            mid_idx = len(years) // 2
            first_half_avg = sum(year_counts[y] for y in years[:mid_idx]) / mid_idx if mid_idx > 0 else 0
            second_half_avg = sum(year_counts[y] for y in years[mid_idx:]) / (len(years) - mid_idx) if len(years) > mid_idx else 0

            if second_half_avg > first_half_avg * 1.2:  # 20% Wachstum
                rising_trends += 1
                skills_with_trend += 1
            elif second_half_avg < first_half_avg * 0.8:  # 20% Rückgang
                falling_trends += 1
                skills_with_trend += 1
            else:
                stable_trends += 1

    # Qualitäts-Score
    validation_score = 0
    if total_skills > 0:
        validation_score = (validated_skills / total_skills) * 100

    # Gap-Rate
    gap_rate = 0
    if validated_skills > 0:
        gap_rate = (skills_with_gaps / validated_skills) * 100

    return {
        'total_skills': total_skills,
        'validated_skills': validated_skills,  # >= 3 Jahre Daten
        'skills_with_gaps': skills_with_gaps,
        'skills_with_trend': skills_with_trend,
        'validation_score': round(validation_score, 1),
        'gap_rate': round(gap_rate, 1),
        'trend_classification': {
            'rising': rising_trends,
            'stable': stable_trends,
            'falling': falling_trends
        },
        'min_years_required': min_years
    }


def build_dashboard_metrics(top_n: int = 10) -> Dict[str, Any]:
    summary = load_summary()
    total_jobs = summary.get('processed') or 0
    total_skills = summary.get('skills_total') or 0
    top_skills = aggregate_top_skills(top_n=top_n)
    domain_mix = aggregate_domain_mix()
    collection_breakdown = aggregate_collection_breakdown()
    time_series = aggregate_time_series_for_skills([s for s, _ in top_skills])

    # Neue Features: Job-Gruppierung nach Rolle
    job_groups = aggregate_jobs_by_role()
    skill_groups = aggregate_skills_by_competence_category()

    # Erweiterte Metriken (DASHBOARD_GUIDE.md Features)
    digital_skills_count = aggregate_digital_skills_count()
    regional_dist = aggregate_regional_distribution()
    emerging_skills = aggregate_emerging_skills(min_year=2024)
    quality_metrics = aggregate_quality_metrics()
    level_progression = aggregate_level_progression()
    pipeline_metrics = aggregate_pipeline_metrics()
    time_series_validation = aggregate_time_series_validation()  # Level 7

    # Role distribution (vereinfacht aus job_groups)
    role_distribution = {k.replace('_', ' ').title(): v['total'] for k, v in job_groups.items()}

    return {
        'total_jobs': total_jobs,
        'total_skills': total_skills,
        'digital_skills_count': digital_skills_count,
        'avg_quality': quality_metrics['avg_quality'],
        'top_skills': [{'skill': s, 'count': c} for s, c in top_skills],
        'domain_mix': domain_mix,
        'collection_breakdown': collection_breakdown,
        'time_series': time_series,
        'job_groups': job_groups,
        'skill_groups': skill_groups,
        'regional_distribution': regional_dist,  # NEU
        'emerging_skills': emerging_skills,  # NEU
        'quality_metrics': quality_metrics,  # NEU
        'level_progression': level_progression,  # NEU
        'pipeline_metrics': pipeline_metrics,  # NEU
        'role_distribution': role_distribution,  # NEU
        'time_series_validation': time_series_validation,  # NEU - Level 7
    }


def aggregate_jobs_by_role() -> Dict[str, Dict[str, Any]]:
    """
    Gruppiert alle Jobs nach ihrer Klassifizierung:
    {
        'software_dev': {
            'total': 15,
            'sub_categories': {'frontend': 5, 'backend': 8, 'devops': 2},
            'top_skills': [...]
        },
        'ux_design': {...},
        ...
    }
    """
    groups = {}
    
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            title = data.get('title', '')
            role = data.get('job_role', '')
            industry = data.get('industry', '')
            
            classification = classify_job_role(title, role, industry)
            category = classification['category']
            sub = classification['sub_category']
            
            if category not in groups:
                groups[category] = {
                    'total': 0,
                    'sub_categories': Counter(),
                    'skills_counter': Counter(),
                }
            
            groups[category]['total'] += 1
            if sub and sub != 'unknown':
                groups[category]['sub_categories'][sub] += 1
            
            # Sammle Skills für diese Rolle
            for c in data.get('competences', []):
                label = c.get('esco_label') or c.get('original_term')
                if label:
                    groups[category]['skills_counter'][label] += 1
        except Exception:
            continue
    
    # Formatiere für JSON-Output
    result = {}
    for cat, data in groups.items():
        top_skills = data['skills_counter'].most_common(5)
        result[cat] = {
            'total': data['total'],
            'sub_categories': dict(data['sub_categories']),
            'top_skills': [{'skill': s, 'count': c} for s, c in top_skills],
        }
    
    return result


def aggregate_skills_by_competence_category() -> Dict[str, Dict[str, Any]]:
    """
    Gruppiert alle Skills nach ihrer Kompetenz-Kategorie:
    {
        'technical_core': {
            'total': 500,
            'skills': [{'name': 'Python', 'count': 45}, ...],
            'roles': {'software_dev': 40, 'data_science': 8, ...}
        },
        ...
    }
    """
    categories = {}
    
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            title = data.get('title', '')
            role = data.get('job_role', '')
            industry = data.get('industry', '')
            job_cat = classify_job_role(title, role, industry)['category']
            
            for c in data.get('competences', []):
                label = c.get('esco_label') or c.get('original_term')
                if not label:
                    continue
                
                collections = c.get('collections', [])
                categorization = categorize_competence(label, collections)
                cat = categorization['category']
                
                if cat not in categories:
                    categories[cat] = {
                        'total': 0,
                        'skills': Counter(),
                        'roles': Counter(),
                    }
                
                categories[cat]['total'] += 1
                categories[cat]['skills'][label] += 1
                categories[cat]['roles'][job_cat] += 1
        except Exception:
            continue
    
    # Formatiere für JSON-Output
    result = {}
    for cat, data in categories.items():
        top_skills = data['skills'].most_common(10)
        top_roles = data['roles'].most_common(5)
        result[cat] = {
            'total': data['total'],
            'top_skills': [{'skill': s, 'count': c} for s, c in top_skills],
            'top_roles': [{'role': r, 'count': c} for r, c in top_roles],
        }
    
    return result
