import pdfplumber
def extract_pdf_text(filepath):
    with pdfplumber.open(filepath) as pdf:
        return '\n'.join([page.extract_text() or '' for page in pdf.pages])
