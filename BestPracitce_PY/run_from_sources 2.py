import argparse, json
from ingest import read_any
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render-js", action="store_true", default=False)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--mode", choices=["w","a"], default="a")
    ap.add_argument("--out", default="out.jsonl")
    ap.add_argument("inputs", nargs="*")
    args = ap.parse_args()
    records = []
    for f in args.inputs:
        rec = read_any(f, render_js=args.render_js)
        if isinstance(rec, list): records.extend(rec)
        else: records.append(rec)
    if args.write or True:
        with open(args.out, args.mode, encoding="utf-8") as fo:
            for r in records: fo.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"Wrote {len(records)} records to {args.out}")
    else:
        for r in records: print(json.dumps(r, ensure_ascii=False))
if __name__ == "__main__": main()