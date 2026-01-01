import io
from app.infrastructure.reporting import build_dashboard_metrics, generate_csv_report


def test_build_dashboard_metrics_structure():
    metrics = build_dashboard_metrics(top_n=5)
    assert 'total_jobs' in metrics
    assert 'total_skills' in metrics
    assert 'top_skills' in metrics
    assert isinstance(metrics['top_skills'], list)


def test_generate_csv_report_not_empty():
    bio = generate_csv_report()
    assert isinstance(bio, io.BytesIO)
    content = bio.getvalue()
    assert len(content) > 0
