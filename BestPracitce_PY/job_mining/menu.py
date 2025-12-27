
import subprocess, sys, os, textwrap, yaml

MENU = """
==================== Job Mining Console (v11.3) ====================
[1] Komplettlauf (sources.yaml)                 -> run_all.py
[2] Pipeline auf beliebige Quellen (mehrzeilig) -> run_from_sources.py
[3] Demo-Run (Fixtures, alle Dateien)           -> run_pipeline.py
[4] Firmen/Branchen-Register bauen              -> company_registry.build_registry
[5] Tests ausführen                             -> pytest
[6] sources.yaml anzeigen                       
[7] HTML-Report erzeugen (Filter+Timeline)      -> report.py
[8] Umgebungscheck (Libs, Tools, Browser)       -> tools/env_check.py
[9] JS-Smoke-Test (Playwright)                  -> ingest.read_any(render_js=True)
[10] ESCO-Aliasdaten aus ZIP bauen              -> esco_loader.py
[0] Beenden
==================================================================
"""

def run(cmd):
    if isinstance(cmd, list):
        print("$ " + " ".join(cmd))
        subprocess.run(cmd, check=False)
    else:
        print("$ " + cmd)
        subprocess.run(cmd, shell=True, check=False)

def main():
    while True:
        print(MENU)
        choice = input("Auswahl [1] ").strip() or "1"
        if choice == "0":
            print("Bye."); return
        elif choice == "1":
            cfg = input("Pfad zu sources.yaml [sources.yaml] ").strip() or "sources.yaml"
            run([sys.executable, "run_all.py", cfg])
        elif choice == "2":
            print('Gib Pfade/URLs **einzeln** ein (Leerzeile beendet). Flags optional in **eigener** Zeile:\n  --render-js  |  --write  |  --mode=w|a')
            entries, flags = [], []
            while True:
                s = input("> ").strip()
                if not s: break
                if s.startswith("--"): flags.append(s)
                else: entries.append(s)
            cfg = {"out":"out.jsonl","mode":"w","render_js":("--render-js" in flags),"inputs":["tests/fixtures"] + entries}
            with open("sources.yaml","w",encoding="utf-8") as f:
                yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)
            print("sources.yaml aktualisiert.")
            args = ["run_from_sources.py"] + (["--render-js"] if "--render-js" in flags else []) + entries
            run([sys.executable] + args)
        elif choice == "3":
            run([sys.executable, "run_pipeline.py"])
        elif choice == "4":
            run([sys.executable, "-c", "import company_registry as c;c.build_registry()"])
        elif choice == "5":
            run([sys.executable, "-m", "pytest", "-q"])
        elif choice == "6":
            p = input("Pfad zu sources.yaml [sources.yaml] ").strip() or "sources.yaml"
            if os.path.exists(p): print(open(p,"r",encoding="utf-8").read())
            else: print("sources.yaml nicht gefunden.")
        elif choice == "7":
            run([sys.executable, "report.py"])
        elif choice == "8":
            run([sys.executable, "tools/env_check.py"])
        elif choice == "9":
            url = input("Test-URL (z.B. StepStone/LinkedIn) [https://example.com] ").strip() or "https://example.com"
            code = f"from ingest import read_any; print(read_any('{url}',render_js=True)['text'][:300])"
            run([sys.executable,"-c",code])
        elif choice == "10":
            path = input("Pfad zur ESCO-ZIP [ESCO*.zip] ").strip() or "ESCO*.zip"
            run([sys.executable, "esco_loader.py", path])
        else:
            print("Ungültige Auswahl.")

if __name__ == "__main__":
    main()
