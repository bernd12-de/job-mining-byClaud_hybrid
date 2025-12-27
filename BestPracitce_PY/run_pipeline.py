
from job_mining.pipeline import process_documents, to_jsonl, enrich_with_esco, load_esco_alias
def main():
    recs=process_documents(["fixtures/anzeigen"], render_js=False)
    recs=enrich_with_esco(recs, load_esco_alias())
    to_jsonl(recs, "out.jsonl", mode="w")
    print(f"Wrote {len(recs)} records to out.jsonl")
if __name__=="__main__": main()
