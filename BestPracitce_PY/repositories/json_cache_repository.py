"""
Data Repository: JSON Cache Repository
Speichert/Lädt JobPostings als JSON
"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from domain.models.job_posting import JobPosting, JobCategory
from domain.models.competence import Competence, CompetenceSource, CompetenceType


class JSONCacheRepository:
    """
    Repository: JSON-basierter Cache
    
    Speichert JobPostings persistent als JSON
    """
    
    def __init__(self, cache_path: str = "data/cache/jobs.json"):
        self.cache_path = Path(cache_path)
        
        # Erstelle Verzeichnis falls nicht vorhanden
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save_all(self, jobs: List[JobPosting]) -> None:
        """Speichere alle Jobs im Cache"""
        data = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'count': len(jobs),
            'jobs': [self._job_to_dict(job) for job in jobs]
        }
        
        with open(self.cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {len(jobs)} Jobs in Cache gespeichert: {self.cache_path}")
    
    def load_all(self) -> List[JobPosting]:
        """Lade alle Jobs aus Cache"""
        if not self.cache_path.exists():
            print(f"⚠️ Kein Cache gefunden: {self.cache_path}")
            return []
        
        with open(self.cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        jobs = [self._dict_to_job(job_dict) for job_dict in data['jobs']]
        
        print(f"✅ {len(jobs)} Jobs aus Cache geladen: {self.cache_path}")
        return jobs
    
    def _job_to_dict(self, job: JobPosting) -> dict:
        """Konvertiere JobPosting zu Dict"""
        return {
            'id': job.id,
            'file_name': job.file_name,
            'source': job.source,
            'file_type': job.file_type,
            'job_title': job.job_title,
            'organization': job.organization,
            'location': job.location,
            'year': job.year,
            'remote': job.remote,
            'job_categories': [cat.value for cat in job.job_categories],
            'tasks': job.tasks,
            'requirements': job.requirements,
            # NEU: Stufe 3
            'salary_min': job.salary_min,
            'salary_max': job.salary_max,
            'experience_years_min': job.experience_years_min,
            'experience_years_max': job.experience_years_max,
            'education_level': job.education_level,
            'languages': job.languages,
            'competences': [self._comp_to_dict(c) for c in job.competences],
            'created_at': job.created_at.isoformat(),
        }
    
    def _dict_to_job(self, data: dict) -> JobPosting:
        """Konvertiere Dict zu JobPosting"""
        # Kategorien
        categories = []
        for cat_str in data.get('job_categories', []):
            try:
                categories.append(JobCategory(cat_str))
            except:
                pass
        
        # Job erstellen
        job = JobPosting(
            id=data['id'],
            file_name=data['file_name'],
            source=data['source'],
            raw_text='[cached]',
            file_type=data['file_type'],
            job_title=data.get('job_title'),
            organization=data.get('organization'),
            location=data.get('location'),
            year=data.get('year'),
            remote=data.get('remote'),
            job_categories=categories,
        )
        
        # Tasks & Requirements
        job.tasks = data.get('tasks', [])
        job.requirements = data.get('requirements', [])
        
        # NEU: Stufe 3
        job.salary_min = data.get('salary_min')
        job.salary_max = data.get('salary_max')
        job.experience_years_min = data.get('experience_years_min')
        job.experience_years_max = data.get('experience_years_max')
        job.education_level = data.get('education_level')
        job.languages = data.get('languages', {})
        
        # Kompetenzen
        for comp_dict in data.get('competences', []):
            comp = self._dict_to_comp(comp_dict)
            job.competences.append(comp)
        
        return job
    
    def _comp_to_dict(self, comp: Competence) -> dict:
        """Konvertiere Competence zu Dict"""
        return {
            'name': comp.name,
            'category': comp.category,
            'competence_type': comp.competence_type.value,
            'source': comp.source.value,
            'esco_uri': comp.esco_uri,
            'esco_code': comp.esco_code,
            'alternative_labels': comp.alternative_labels,
            'confidence_score': comp.confidence_score,
        }
    
    def _dict_to_comp(self, data: dict) -> Competence:
        """Konvertiere Dict zu Competence"""
        return Competence(
            name=data['name'],
            category=data['category'],
            competence_type=CompetenceType(data['competence_type']),
            source=CompetenceSource(data['source']),
            esco_uri=data.get('esco_uri'),
            esco_code=data.get('esco_code'),
            alternative_labels=data.get('alternative_labels', []),
            confidence_score=data.get('confidence_score', 1.0),
        )
    
    def exists(self) -> bool:
        """Existiert Cache?"""
        return self.cache_path.exists()
    
    def clear(self) -> None:
        """Lösche Cache"""
        if self.cache_path.exists():
            self.cache_path.unlink()
            print(f"🗑️  Cache gelöscht: {self.cache_path}")
