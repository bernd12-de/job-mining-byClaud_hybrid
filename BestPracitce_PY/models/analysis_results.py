
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class CompetenceTrend:
    competence_name: str
    category: str
    time_periods: List[str] = field(default_factory=list)
    frequencies: List[int] = field(default_factory=list)
    percentages: List[float] = field(default_factory=list)
    trend_direction: str = "stable"
    growth_rate: float = 0.0
    mean_frequency: float = 0.0
    std_deviation: float = 0.0

    def calculate_trend(self):
        if len(self.frequencies) < 2:
            return
        first_half = sum(self.frequencies[:len(self.frequencies)//2])
        second_half = sum(self.frequencies[len(self.frequencies)//2:])
        if first_half > 0:
            self.growth_rate = ((second_half - first_half) / first_half) * 100
            if self.growth_rate > 20:
                self.trend_direction = "rising"
            elif self.growth_rate < -20:
                self.trend_direction = "falling"

@dataclass
class BranchProfile:
    branch_name: str
    job_ads_count: int = 0
    top_competences: List[tuple] = field(default_factory=list)
    avg_competences_per_ad: float = 0.0

    def calculate_metrics(self, job_ads):
        self.job_ads_count = len(job_ads)
        from collections import Counter
        all_comps = []
        for job in job_ads:
            all_comps.extend([c.name for c in job.competences])
        self.top_competences = Counter(all_comps).most_common(15)
        self.avg_competences_per_ad = len(all_comps) / len(job_ads) if job_ads else 0

@dataclass
class RoleProfile:
    role_name: str
    job_category: str
    job_ads_count: int = 0
    required_competences: List[tuple] = field(default_factory=list)
    technical_skills: List[str] = field(default_factory=list)
    methodological_skills: List[str] = field(default_factory=list)
    soft_skills: List[str] = field(default_factory=list)

@dataclass
class TimeSeriesAnalysis:
    start_date: datetime
    end_date: datetime
    competence_trends: List[CompetenceTrend] = field(default_factory=list)
    rising_competences: List[str] = field(default_factory=list)
    falling_competences: List[str] = field(default_factory=list)
    emerging_competences: List[str] = field(default_factory=list)

@dataclass
class ClusterAnalysis:
    method: str
    n_clusters: int
    clusters: List = field(default_factory=list)

@dataclass
class AIInsights:
    model: str
    trend_narratives: Dict[str, str] = field(default_factory=dict)
    cluster_descriptions: Dict[str, str] = field(default_factory=dict)
    transformation_assessment: str = ""
    curriculum_recommendations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0

@dataclass
class AnalysisReport:
    total_job_ads: int
    date_range: tuple
    branches_covered: List[str]
    time_series: Optional[TimeSeriesAnalysis] = None
    branch_profiles: List[BranchProfile] = field(default_factory=list)
    role_profiles: List[RoleProfile] = field(default_factory=list)
    cluster_analysis: Optional[ClusterAnalysis] = None
    ai_insights: Optional[AIInsights] = None
    data_quality_score: float = 0.0
    esco_coverage: float = 0.0
    extraction_accuracy: float = 0.0
