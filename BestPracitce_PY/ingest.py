
import os, io, re, json, logging, mimetypes, subprocess, shutil, pathlib
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
from .normalize import parse_date
try:
    from pdfminer import settings as _pdfminer_settings
    _pdfminer_settings.STRICT=False
    logging.getLogger("pdfminer").setLevel(logging.ERROR)
except Exception: pass
def read_txt(p): return open(p,"r",encoding="utf-8",errors="ignore").read()
def read_docx_text(p):
    try:
        import docx; d=docx.Document(p); return "\n".join([x.text for x in d.paragraphs])
    except Exception: return ""
def _pdftotext(path):
    if shutil.which("pdftotext"):
        try:
            out=subprocess.run(["pdftotext","-layout","-q",path,"-"],check=True,capture_output=True)
            return out.stdout.decode("utf-8","ignore")
        except Exception: return ""
    return ""
def _pdfminer(path):
    try:
        from pdfminer.high_level import extract_text
        return extract_text(path) or ""
    except Exception: return ""
def _ocr_pdf(path):
    try:
        from pdf2image import convert_from_path; import pytesseract
        pages=convert_from_path(path, dpi=200); chunks=[]
        for im in pages[:5]: chunks.append(pytesseract.image_to_string(im))
        return "\n".join(chunks)
    except Exception: return ""
def read_pdf_text(p):
    for fn in (_pdftotext,_pdfminer,_ocr_pdf):
        t=fn(p)
        if t and t.strip(): return t
    return ""
def read_html(url, render_js=False):
    try:
        r=requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"}); r.raise_for_status(); return r.text
    except Exception: return ""
def html_to_text(html):
    soup=BeautifulSoup(html or "","html.parser")
    for x in soup(["script","style","noscript"]): x.extract()
    t=soup.get_text("\n")
    t=re.sub(r"\n\s*\n","\n",t); return t.strip()
TITLE_RE=re.compile(r'^.{6,120}$')
def parse_text_to_record(doc_id, text):
    lines=[ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    title=next((ln for ln in lines if TITLE_RE.match(ln)),"Unknown")
    company="Unknown"
    for ln in lines[1:4]:
        if ln!=title and len(ln)<=80: company=ln; break
    iso, src, prec = parse_date(text)
    return {"id":doc_id,"title":title,"company":company,"posting_date_iso":iso,"posting_date_source":src,"posting_date_precision":prec,"tools":[],"methods":[],"fields":{"skills_esco":[]},"text":(text or "")[:10000]}
def is_url(x):
    try:
        u=urlparse(x); return bool(u.scheme and u.netloc)
    except Exception: return False
def read_any(x, render_js=False):
    if os.path.isdir(x):
        recs=[]
        for root,_,files in os.walk(x):
            for fn in files:
                p=os.path.join(root,fn)
                if fn.lower().endswith((".txt",".pdf",".docx",".html",".htm")):
                    recs.append(read_any(p, render_js=render_js))
        return {"_batch":True,"records":recs}
    if os.path.isfile(x):
        ext=pathlib.Path(x).suffix.lower()
        if ext==".txt":
            t=read_txt(x); r=parse_text_to_record(os.path.basename(x), t); r["text"]=t; return r
        if ext==".pdf":
            t=read_pdf_text(x); r=parse_text_to_record(os.path.basename(x), t); r["text"]=t; return r
        if ext==".docx":
            t=read_docx_text(x); r=parse_text_to_record(os.path.basename(x), t); r["text"]=t; return r
        if ext in (".html",".htm"):
            t=html_to_text(read_txt(x)); r=parse_text_to_record(os.path.basename(x), t); r["text"]=t; return r
        t=read_txt(x); r=parse_text_to_record(os.path.basename(x), t); r["text"]=t; return r
    if is_url(x):
        html=read_html(x, render_js=render_js); text=html_to_text(html)
        return parse_text_to_record(x, text)
    raise FileNotFoundError(x)
