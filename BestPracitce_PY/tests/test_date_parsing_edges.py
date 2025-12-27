
from job_mining.normalize import parse_date
from datetime import datetime, timezone, timedelta
BERLIN = timezone(timedelta(hours=1))
now = datetime(2025,11,7,12,0,tzinfo=BERLIN)

cases = [
    ("Stand: Oktober 2023", "2023-10-15"),
    ("ab sofort", None),  # may be implicit; parser returns None (acceptable here)
    ("as of 03/24", "2024-03-15"),
]
for text, want in cases:
    iso, src, prec = parse_date(text, now_utc=now)
    if want is None:
        assert iso is None
    else:
        assert iso == want, (text, iso, want)
print("OK date edges")
