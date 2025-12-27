
from job_mining.skill_filter import extract_skills
neg = "Wir suchen dich! Du bist motiviert und wir bieten dir viel. Unser Team liebt Kaffee."
skills = extract_skills(neg)
assert "wir" not in [s.lower() for s in skills]
assert "du" not in [s.lower() for s in skills]
print("OK negative skill filter")
