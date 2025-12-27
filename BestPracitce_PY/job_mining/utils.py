import functools, datetime, os
def log_path():
    os.makedirs("logs", exist_ok=True)
    return os.path.join("logs", f"run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
def safe_run(func):
    def _wrap(*a, **kw):
        try: return func(*a, **kw)
        except Exception as e:
            lp = log_path()
            open(lp,"w",encoding="utf-8").write(str(e))
            print("Log:", lp); raise
    return _wrap