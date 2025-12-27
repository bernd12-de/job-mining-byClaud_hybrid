
import os, re
from bs4 import BeautifulSoup
import requests
try:
    from pdfminer.high_level import extract_text as pdf_extract_text
except Exception:
    pdf_extract_text = None

def read_txt(p):
    with open(p,"r",encoding="utf-8",errors="ignore") as f:
        return f.read()

def read_html(url):
    r = requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for s in soup(["script","style","noscript"]): s.decompose()
    return soup.get_text(" ", strip=True)

def read_pdf(p):
    if pdf_extract_text is None: return ""
    return pdf_extract_text(p) or ""

def read_docx_text(p):
    try:
        import docx
        doc = docx.Document(p)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception:
        return ""

def parse_text_to_record(source_id, text):
    head = (text or "")[:200]
    m_title = re.search(r'([A-ZÄÖÜ].{5,80}?)(?:\s[-–]|\s\(|\sbei|\sat|\s–|$)', head)
    title = m_title.group(1).strip() if m_title else None
    m_company = re.search(r'\b([A-Z][A-Za-zÄÖÜäöüß&\.\- ]{2,40})\b', head)
    company = m_company.group(1).strip() if m_company else None
    return {"id": source_id, "title": title, "company": company, "text": (text or "")[:5000]}

def read_any(x, render_js=False):
    x = x.strip()
    if x.startswith("http://") or x.startswith("https://"):
        t = read_html(x); r = parse_text_to_record(x, t); return r
    if os.path.isdir(x):
        out = []
        for root, _, files in os.walk(x):
            for fn in files:
                p = os.path.join(root, fn); lo = fn.lower()
                if lo.endswith(".txt"):
                    t = read_txt(p); r = parse_text_to_record(os.path.basename(p), t); out.append(r)
                elif lo.endswith(".pdf"):
                    t = read_pdf(p); r = parse_text_to_record(os.path.basename(p), t); out.append(r)
                elif lo.endswith(".docx"):
                    t = read_docx_text(p); r = parse_text_to_record(os.path.basename(p), t); out.append(r)
        return out
    if os.path.isfile(x):
        lo = x.lower()
        if lo.endswith(".txt"):
            t = read_txt(x); r = parse_text_to_record(os.path.basename(x), t); return r
        if lo.endswith(".pdf"):
            t = read_pdf(x); r = parse_text_to_record(os.path.basename(x), t); return r
        if lo.endswith(".docx"):
            t = read_docx_text(x); r = parse_text_to_record(os.path.basename(x), t); return r
    raise FileNotFoundError(x)
