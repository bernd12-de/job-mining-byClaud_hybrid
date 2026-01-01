"""
Test: Organization & Branch Extraction (Best Practice Integration)

Testet die erweiterte Company Name Extraction und Branch Mapping.
"""
import pytest
from app.infrastructure.extractor.metadata_extractor import MetadataExtractor


class TestOrganizationBranchExtraction:
    """Test Suite für Company & Branch Extraction"""

    def setup_method(self):
        """Setup für jeden Test"""
        self.extractor = MetadataExtractor()

    def test_company_with_suffix_gmb_h(self):
        """Test: Company mit GmbH Suffix"""
        text = "Wir sind die TechCorp GmbH und suchen einen Developer"
        result = self.extractor._extract_organization(text)
        assert "TechCorp GmbH" in result
        assert result != "Unbekannte Firma"

    def test_company_with_suffix_ag(self):
        """Test: Company mit AG Suffix"""
        text = "BMW AG bietet eine Stelle als Senior Engineer"
        result = self.extractor._extract_organization(text)
        assert "BMW AG" in result

    def test_company_hint_bei(self):
        """Test: 'bei FIRMA' Pattern"""
        text = "Senior Developer bei SAP Deutschland"
        result = self.extractor._extract_organization(text)
        assert "SAP" in result or "Deutschland" in result

    def test_company_hint_sucht(self):
        """Test: 'FIRMA sucht' Pattern"""
        text = "Google sucht einen UX Designer in München"
        result = self.extractor._extract_organization(text)
        # Should extract "Google" but not "UX Designer"
        assert "Google" in result
        assert "UX Designer" not in result

    def test_branch_automotive(self):
        """Test: Branch Mapping - Automotive"""
        branch = self.extractor._extract_branch("BMW AG", "")
        assert branch == "Automotive"

        branch = self.extractor._extract_branch("Volkswagen Group", "")
        assert branch == "Automotive"

        branch = self.extractor._extract_branch("Porsche AG", "")
        assert branch == "Automotive"

    def test_branch_finance(self):
        """Test: Branch Mapping - Finanzen"""
        branch = self.extractor._extract_branch("Deutsche Bank AG", "")
        assert branch == "Finanzen & Versicherung"

        branch = self.extractor._extract_branch("Sparkasse München", "")
        assert branch == "Finanzen & Versicherung"

    def test_branch_technology(self):
        """Test: Branch Mapping - IT & Software"""
        branch = self.extractor._extract_branch("SAP SE", "")
        assert branch == "IT & Software"

        branch = self.extractor._extract_branch("Cloud Solutions GmbH", "")
        assert branch == "IT & Software"

    def test_branch_consulting(self):
        """Test: Branch Mapping - Consulting"""
        branch = self.extractor._extract_branch("McKinsey & Company", "")
        assert branch == "Consulting"

        branch = self.extractor._extract_branch("Beratungshaus XYZ", "")
        assert branch == "Consulting"

    def test_branch_fallback_from_text(self):
        """Test: Branch Fallback aus Text wenn Company unknown"""
        text = "Wir sind ein Technologie-Unternehmen im Bereich Cloud Computing"
        branch = self.extractor._extract_branch("Unbekannte Firma", text)
        assert branch == "IT & Software"

    def test_branch_unknown_fallback(self):
        """Test: Fallback für unbekannte Branchen"""
        branch = self.extractor._extract_branch("Mysterious Corp", "")
        assert branch == "Sonstige Branchen"

    def test_integration_extract_all(self):
        """Test: Integration in extract_all()"""
        text = """
        BMW AG
        Senior Backend Developer (m/w/d)
        München
        Stand: Oktober 2024

        Wir suchen einen erfahrenen Java Developer.
        """
        result = self.extractor.extract_all(text, "bmw_job.pdf", "")

        # Company sollte erkannt werden
        assert result.get("company_name") == "BMW AG"

        # Branch sollte Automotive sein
        assert result.get("industry") == "Automotive"

        # Weitere Metadaten sollten funktionieren
        assert result.get("region") == "München"
        assert "2024" in result.get("posting_date", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
