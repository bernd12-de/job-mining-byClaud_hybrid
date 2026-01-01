import pytest
from app.domain.models import CompetenceDTO

def test_model_datatypes():
    """Prüft, ob die Typen für die Datenbank-Migration korrekt sind."""
    dto = CompetenceDTO(
        original_term="Microservices",
        esco_label="Softwarearchitektur",
        esco_uri="http://data.europa.eu/esco/node/123",
        confidence_score=0.95,
        level=4, # Wir testen hier explizit den Integer!
        is_digital=True,
        source_domain="Fachbuch_Starke"
    )

    assert isinstance(dto.level, int), "Level muss ein Integer für SQL sein!"
    assert dto.is_digital is True
    print(f"\n✅ Modell-Validierung erfolgreich: {dto.json()}")
