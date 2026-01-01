from app.infrastructure.reporting import generate_pdf_report


def test_generate_pdf_report():
    bio = generate_pdf_report()
    data = bio.getvalue()
    # PDF-Dateien beginnen normalerweise mit %PDF
    assert data.startswith(b"%PDF")
