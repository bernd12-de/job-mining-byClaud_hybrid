
import json, os
from tests.testcases import load_docs
from job_mining.pipeline import process_documents

BASE = os.path.dirname(os.path.dirname(__file__))
GOLD_PATH = os.path.join(BASE, "gold", "jobs_gold.json")
GOLD = json.load(open(GOLD_PATH,"r",encoding="utf-8"))

posts = process_documents(load_docs())
by_id = {p.source_id: p for p in posts}

def assert_contains(haystack, needles):
    hl = [s.lower() if isinstance(s,str) else s for s in haystack]
    for n in needles:
        assert any((n.lower() if isinstance(n,str) else n) in h for h in hl) or n in haystack, (needles, haystack)

for case in GOLD:
    pid = case["id"]; exp = case["expect"]; p = by_id.get(pid)
    assert p is not None, pid
    if "company" in exp:
        assert (p.company or "") == exp["company"], (pid, p.company, exp["company"])
    if "skills_esco_contains" in exp:
        ids = [e["id"] for e in (p.fields.get("skills_esco") or [])]
        for need in exp["skills_esco_contains"]:
            assert need in ids, (pid, ids, need)

print("OK gold compare")
