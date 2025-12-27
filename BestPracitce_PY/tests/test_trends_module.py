
import os, json
from tests.testcases import load_docs
from job_mining.pipeline import process_documents, to_jsonl
from company_registry.build_registry import aggregate_from_jsonl

posts = process_documents(load_docs())
tmp = "tmp_out.jsonl"
open(tmp,"w",encoding="utf-8").write(to_jsonl(posts))
companies, industries = aggregate_from_jsonl(tmp, company_industry_map={})
assert isinstance(companies, dict) and isinstance(industries, dict)
os.remove(tmp)
print("OK trends smoke")
