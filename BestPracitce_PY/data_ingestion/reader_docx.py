from docx import Document
def extract_docx_text(filepath):
    doc = Document(filepath)
    return '\n'.join([p.text for p in doc.paragraphs])
