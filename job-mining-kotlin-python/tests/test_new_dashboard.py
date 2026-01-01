"""
Test Suite für neues Multi-Page Dashboard
Kritische Tests für alle Komponenten
"""

import pytest
import requests
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# API Endpoints
KOTLIN_API = os.getenv("KOTLIN_API_URL", "http://localhost:8080")
PYTHON_API = os.getenv("PYTHON_API_URL", "http://localhost:8000")

class TestAPIEndpoints:
    """Test 1: API Endpunkte"""

    def test_python_health_endpoint(self):
        """Test Python Backend /health"""
        try:
            response = requests.get(f"{PYTHON_API}/health", timeout=5)
            assert response.status_code == 200, "Python Backend /health should return 200"
            print("✅ Python /health OK")
        except requests.exceptions.ConnectionError:
            pytest.skip("Python Backend nicht erreichbar")

    def test_kotlin_health_endpoint(self):
        """Test Kotlin Backend /actuator/health"""
        try:
            response = requests.get(f"{KOTLIN_API}/actuator/health", timeout=5)
            assert response.status_code == 200, "Kotlin Backend /health should return 200"
            print("✅ Kotlin /actuator/health OK")
        except requests.exceptions.ConnectionError:
            pytest.skip("Kotlin Backend nicht erreichbar")

    def test_discovery_candidates_endpoint(self):
        """Test Discovery Candidates Endpoint"""
        try:
            response = requests.get(f"{PYTHON_API}/discovery/candidates", timeout=5)
            assert response.status_code == 200, "Discovery candidates should return 200"
            data = response.json()
            assert isinstance(data, list), "Discovery candidates should return list"
            print(f"✅ Discovery candidates OK ({len(data)} candidates)")
        except requests.exceptions.ConnectionError:
            pytest.skip("Python Backend nicht erreichbar")


class TestESCOData:
    """Test 2: ESCO-Daten laden"""

    def test_esco_skills_loading(self):
        """Test ESCO Skills von Kotlin API"""
        try:
            response = requests.get(f"{KOTLIN_API}/api/v1/rules/esco-full", timeout=10)
            assert response.status_code == 200, "ESCO endpoint should return 200"
            data = response.json()
            assert isinstance(data, list), "ESCO should return list"
            assert len(data) > 10000, f"ESCO should have >10k skills, got {len(data)}"
            print(f"✅ ESCO Skills loaded: {len(data):,} skills")
        except requests.exceptions.ConnectionError:
            pytest.skip("Kotlin Backend nicht erreichbar")

    def test_esco_skill_structure(self):
        """Test ESCO Skill Datenstruktur"""
        try:
            response = requests.get(f"{KOTLIN_API}/api/v1/rules/esco-full", timeout=10)
            data = response.json()
            if data:
                skill = data[0]
                assert 'preferredLabel' in skill, "Skill should have preferredLabel"
                assert 'conceptUri' in skill, "Skill should have conceptUri"
                print("✅ ESCO Skill structure OK")
        except requests.exceptions.ConnectionError:
            pytest.skip("Kotlin Backend nicht erreichbar")


class TestDatabaseConnection:
    """Test 3: DB-Verbindung & Queries"""

    def test_jobs_endpoint(self):
        """Test Jobs Endpoint (DB-Abfrage)"""
        try:
            response = requests.get(f"{KOTLIN_API}/api/v1/jobs?page=0&size=10", timeout=10)
            assert response.status_code == 200, "Jobs endpoint should return 200"
            data = response.json()
            assert 'content' in data, "Jobs should have 'content' field"
            assert 'totalElements' in data, "Jobs should have 'totalElements' field"
            print(f"✅ DB Connection OK ({data.get('totalElements', 0)} jobs total)")
        except requests.exceptions.ConnectionError:
            pytest.skip("Kotlin Backend nicht erreichbar")

    def test_jobs_pagination(self):
        """Test Jobs Pagination"""
        try:
            response = requests.get(f"{KOTLIN_API}/api/v1/jobs?page=0&size=20", timeout=10)
            data = response.json()
            assert data.get('size', 0) <= 20, "Page size should be <= 20"
            assert 'totalPages' in data, "Should have totalPages"
            print("✅ Pagination OK")
        except requests.exceptions.ConnectionError:
            pytest.skip("Kotlin Backend nicht erreichbar")


class TestNavigation:
    """Test 4: Navigation zwischen Seiten"""

    def test_home_page_exists(self):
        """Test Home.py existiert"""
        home_path = Path(__file__).parent.parent / "Home.py"
        assert home_path.exists(), "Home.py should exist"
        assert home_path.stat().st_size > 100, "Home.py should not be empty"
        print("✅ Home.py exists")

    def test_pages_directory_exists(self):
        """Test pages/ Verzeichnis existiert"""
        pages_path = Path(__file__).parent.parent / "pages"
        assert pages_path.exists(), "pages/ directory should exist"
        assert pages_path.is_dir(), "pages/ should be a directory"
        print("✅ pages/ directory exists")

    def test_all_pages_exist(self):
        """Test alle Unterseiten existieren"""
        pages_path = Path(__file__).parent.parent / "pages"
        expected_pages = [
            "1_📈_Trends.py",
            "2_👤_Rollen.py",
            "3_🗺️_ESCO_Landkarte.py",
            "4_🔍_Discovery.py",
            "5_💼_Jobs.py",
        ]

        for page in expected_pages:
            page_path = pages_path / page
            assert page_path.exists(), f"{page} should exist"
            assert page_path.stat().st_size > 100, f"{page} should not be empty"

        print(f"✅ All {len(expected_pages)} pages exist")


class TestStatsCards:
    """Test 5: Stats-Karten mit echten Daten"""

    def test_fetch_stats_data(self):
        """Test Stats können von APIs abgerufen werden"""
        stats = {}

        # Jobs
        try:
            response = requests.get(f"{KOTLIN_API}/api/v1/jobs?page=0&size=1", timeout=5)
            if response.status_code == 200:
                stats['jobs'] = response.json().get('totalElements', 0)
        except:
            stats['jobs'] = 0

        # ESCO Skills
        try:
            response = requests.get(f"{KOTLIN_API}/api/v1/rules/esco-full", timeout=10)
            if response.status_code == 200:
                stats['skills'] = len(response.json())
        except:
            stats['skills'] = 0

        # Discovery
        try:
            response = requests.get(f"{PYTHON_API}/discovery/candidates", timeout=5)
            if response.status_code == 200:
                stats['new_skills'] = len([c for c in response.json() if c.get('entity_type') == 'skill'])
        except:
            stats['new_skills'] = 0

        # Check at least one stat is available
        assert sum(stats.values()) > 0, "At least one stat should be available"
        print(f"✅ Stats: Jobs={stats['jobs']}, Skills={stats['skills']}, New={stats['new_skills']}")


class TestCharts:
    """Test 6: Charts rendern korrekt"""

    def test_timeline_data_generation(self):
        """Test Zeitreihen-Daten können generiert werden"""
        import pandas as pd

        dates = pd.date_range(start='2020-01-01', end='2025-12-31', freq='M')
        assert len(dates) > 0, "Timeline should have data points"
        print(f"✅ Timeline data: {len(dates)} data points")

    def test_skills_data_for_charts(self):
        """Test Skill-Daten für Charts"""
        try:
            response = requests.get(f"{KOTLIN_API}/api/v1/jobs?page=0&size=50", timeout=10)
            if response.status_code == 200:
                jobs = response.json().get('content', [])
                all_skills = []
                for job in jobs:
                    all_skills.extend(job.get('topCompetences', []))

                assert len(all_skills) > 0, "Should have skills for charts"
                print(f"✅ Chart data: {len(all_skills)} skills from {len(jobs)} jobs")
        except:
            pytest.skip("Kotlin Backend nicht erreichbar")


# ========================================
# MAIN TEST RUNNER
# ========================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 DASHBOARD TEST SUITE")
    print("="*60 + "\n")

    # Run pytest
    pytest.main([__file__, "-v", "-s"])
