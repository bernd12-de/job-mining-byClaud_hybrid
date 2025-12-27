import pytesseract
from pdf2image import convert_from_path
import tempfile, os

def extract_ocr_text(filepath):
    text = ""
    with tempfile.TemporaryDirectory() as path:
        images = convert_from_path(filepath, output_folder=path)
        for img in images:
            text += pytesseract.image_to_string(img, lang='deu') + "\n"
    return text
