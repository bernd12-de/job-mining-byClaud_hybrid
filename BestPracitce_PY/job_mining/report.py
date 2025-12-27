import json, os, datetime
from company_registry import aggregate_from_jsonl
def main(out="out.jsonl", html="report.html"):
    if not os.path.exists(out):
        print("out.jsonl fehlt. Bitte erst eine Pipeline laufen lassen."); return
    agg = aggregate_from_jsonl(out)
    rows = "".join(f"<tr><td>{c}</td><td>{n}</td></tr>" for c,n in sorted(agg["companies"].items(), key=lambda x:(-x[1],x[0])))
    html_s = f"<!doctype html><meta charset='utf-8'><h1>Job-Mining Report (v11.3)</h1><p>Stand: {datetime.datetime.now().isoformat(timespec='seconds')}</p><table border=1 cellpadding=6><tr><th>Firma</th><th>Count</th></tr>{rows}</table>"
    open(html,"w",encoding="utf-8").write(html_s); print("Report geschrieben:", html)
if __name__ == "__main__": main()