import sys, platform, importlib, shutil
PKGS = {
    "yaml": "pyyaml","bs4":"beautifulsoup4","requests":"requests","PyPDF2":"PyPDF2",
    "pdfminer.high_level":"pdfminer.six","PIL":"Pillow","pdf2image":"pdf2image",
    "pytesseract":"pytesseract","playwright":"playwright","pytest":"pytest","docx":"python-docx",
}
print(f"Python: {sys.executable}"); print(f"Version: {platform.python_version()}"); print(f"Platform: {platform.platform()}")
for mod, pipname in PKGS.items():
    try: importlib.import_module(mod); print(f"{mod:<20}-> OK (pip: {pipname})")
    except Exception: print(f"{mod:<20}-> FEHLT (pip install {pipname})")
print("\nSystem tools:")
for tool in ["pdftotext","tesseract"]:
    path = shutil.which(tool); print(f"{tool:<10} -> {path or 'NOT FOUND'}")
print("\nmacOS tips: brew install poppler tesseract ; python3 -m playwright install chromium")