
import glob, os, json
from job_mining.pipeline import process_documents, to_jsonl

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")

def load_docs():
    docs = []
    for path in sorted(glob.glob(os.path.join(FIXTURE_DIR, "*.txt"))):
        with open(path, "r", encoding="utf-8") as f:
            docs.append({"id": os.path.basename(path), "text": f.read()})
    return docs

if __name__ == "__main__":
    docs = load_docs()
    posts = process_documents(docs)
    out = to_jsonl(posts)
    out_path = os.path.join(os.path.dirname(__file__), "..", "out.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Wrote {len(posts)} records to {out_path}")
