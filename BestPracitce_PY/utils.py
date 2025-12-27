
import os, sys, datetime, functools
def ensure_dirs(): os.makedirs("logs", exist_ok=True); os.makedirs("data", exist_ok=True)
def log_path(prefix="run"):
    ensure_dirs(); ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join("logs", f"{prefix}_{ts}.log")
def safe_main(fn):
    @functools.wraps(fn)
    def _wrap(*a, **kw):
        ensure_dirs(); logf = log_path(prefix=fn.__name__)
        try: return fn(*a, **kw)
        except SystemExit: raise
        except Exception as e:
            open(logf,"w",encoding="utf-8").write(f"Exception: {e}\n"); raise
    return _wrap
