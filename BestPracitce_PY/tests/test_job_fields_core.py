
from tests.testcases import load_docs
from job_mining.extract_fields import extract_all
docs = load_docs()
for d in docs:
    f = extract_all(d["text"], d["id"])
    assert f["company"] is None or isinstance(f["company"], str)
    assert "posting_date_precision" in f
print("OK job fields core")
