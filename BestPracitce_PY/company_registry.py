import json, os
def build_registry():
    os.makedirs("data", exist_ok=True)
    reg = {"companies": ["PwC Deutschland","Lingoda GmbH"]}
    with open("data/company_registry.json","w",encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
    print("Registry written.")
def aggregate_from_jsonl(path="out.jsonl"):
    items = [json.loads(line) for line in open(path, "r", encoding="utf-8") if line.strip()]
    by_company = {}
    for it in items:
        c = (it.get("company") or "UNKNOWN").strip()
        by_company[c] = by_company.get(c, 0) + 1
    return {"companies": by_company, "total": len(items)}