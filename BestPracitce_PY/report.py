
import json, collections, html
def read_jsonl(p):
    return [json.loads(x) for x in open(p,"r",encoding="utf-8") if x.strip()]
def make_report(rows):
    by_month=collections.Counter(); esco=collections.Counter()
    for r in rows:
        d=(r.get("posting_date_iso") or "0000-00-00")[:7]; by_month[d]+=1
        for s in r.get("fields",{}).get("skills_esco",[]): esco[s]+=1
    H=["<html><head><meta charset='utf-8'><title>Report</title><style>body{font-family:system-ui;margin:20px}table{border-collapse:collapse}td,th{border:1px solid #ddd;padding:6px}</style></head><body>"]
    H+=["<h1>Job Mining Report</h1>","<h2>Timeline</h2><table><tr><th>Monat</th><th>Count</th></tr>"]
    for k in sorted(by_month): H.append(f"<tr><td>{html.escape(k)}</td><td>{by_month[k]}</td></tr>")
    H+=["</table><h2>Top ESCO-Skills</h2><table><tr><th>Skill</th><th>Count</th></tr>"]
    for k,v in esco.most_common(30): H.append(f"<tr><td>{html.escape(k)}</td><td>{v}</td></tr>")
    H+=["</table><h2>Dokumente</h2><table><tr><th>ID</th><th>Titel</th><th>Firma</th><th>Datum</th></tr>"]
    for r in rows[:200]:
        H.append(f"<tr><td>{html.escape(str(r.get('id','')))}</td><td>{html.escape(r.get('title',''))}</td><td>{html.escape(r.get('company',''))}</td><td>{html.escape(str(r.get('posting_date_iso','')))}</td></tr>")
    H+=["</table></body></html>"]
    return "\n".join(H)
def main():
    rows=read_jsonl("out.jsonl"); open("report.html","w",encoding="utf-8").write(make_report(rows)); print("Report: report.html")
if __name__=="__main__": main()
