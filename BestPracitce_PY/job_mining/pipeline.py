from .types import Post
from .normalize import parse_date
from .skill_filter import extract_skills
def process_documents(docs):
    posts = []
    for d in docs:
        text = d.text or ""
        first = (text.strip().splitlines()+[''])[0]
        title = first.strip()[:80] or None
        company = None
        iso, src, prec = parse_date(text)
        posts.append(Post(
            source_id=d.source_id, title=title, company=company,
            posting_date_iso=iso, posting_date_source=src, posting_date_precision=prec,
            tools=[], methods=[], fields={"skills_esco": extract_skills(text)}, text=text[:2000]
        ))
    return posts