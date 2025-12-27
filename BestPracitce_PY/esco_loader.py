
import sys, glob, json, zipfile, os
def load_from_zip(zip_glob):
    matches=glob.glob(zip_glob)
    if not matches: raise FileNotFoundError(zip_glob)
    zf=matches[0]; aliases={}
    with zipfile.ZipFile(zf) as z:
        for name in z.namelist():
            if name.lower().endswith(".csv") and ("skill" in name.lower() or "concept" in name.lower() or "class" in name.lower()):
                with z.open(name) as f:
                    text=f.read().decode("utf-8","ignore")
                    for line in text.splitlines()[1:8000]:
                        cols=[c.strip().strip('"') for c in line.split(";")]
                        for c in cols:
                            if c and len(c)<=60: aliases.setdefault(c, c)
    os.makedirs("data", exist_ok=True)
    json.dump(aliases, open("data/esco_alias.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"ESCO-Aliase geschrieben: data/esco_alias.json (Keys: {len(aliases)})")
def main():
    if len(sys.argv)<2: print("Usage: esco_loader.py <ESCO*.zip>"); sys.exit(2)
    load_from_zip(sys.argv[1])
if __name__=="__main__": main()
