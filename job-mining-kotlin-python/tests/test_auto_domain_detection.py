from app.infrastructure.extractor.metadata_extractor import MetadataExtractor


def test_automatic_level_4_assignment():
    extractor = MetadataExtractor()

    # Simuliere einen Pfad aus deinem Projekt
    test_path = "/Users/layher-ad/.../data/source_pdfs/fachbuecher/Gharbi_Architektur.pdf"

    meta = extractor.extract_all("Testinhalt", "Gharbi_Architektur.pdf", test_path)

    assert meta["inferred_level"] == 4
    assert "Fachbuch" in meta["source_domain"]
    print(f"✅ Automatische Erkennung erfolgreich: {meta['source_domain']} -> Level {meta['inferred_level']}")
