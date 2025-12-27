
from job_mining.normalize import parse_date
from datetime import datetime, timezone, timedelta
BERLIN = timezone(timedelta(hours=1))
now = datetime(2025,11,7,12,0,tzinfo=BERLIN)

cases = [
    ("veröffentlicht am 12.03.2024", "2024-03-12"),
    ("Stand: Oktober 2023", "2023-10-15"),
]
for text, want in cases:
    iso, src, prec = parse_date(text, now_utc=now)
    assert iso == want, (text, iso, want)
print("OK date positives")
