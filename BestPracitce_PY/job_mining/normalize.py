import re, datetime
MONTHS = {"januar":1,"jan":1,"jan.":1,"01":1,"februar":2,"feb":2,"feb.":2,"02":2,"märz":3,"maerz":3,"mrz":3,"mär":3,"03":3,"april":4,"apr":4,"apr.":4,"04":4,"mai":5,"05":5,"juni":6,"jun":6,"jun.":6,"06":6,"juli":7,"jul":7,"jul.":7,"07":7,"august":8,"aug":8,"aug.":8,"08":8,"september":9,"sep":9,"sept":9,"sept.":9,"09":9,"oktober":10,"okt":10,"okt.":10,"10":10,"november":11,"nov":11,"nov.":11,"11":11,"dezember":12,"dez":12,"dez.":12,"12":12}
def parse_date(s: str):
    if not s: return (None,None,None)
    s1 = re.sub(r"[|•·]+"," ", s.strip().replace("\u2009"," ").replace("\xa0"," "))
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s1)
    if m:
        y,mn,d = map(int, m.groups()); return (f"{y:04d}-{mn:02d}-{d:02d}","iso","day")
    m = re.search(r"(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{2,4})", s1)
    if m:
        d,mn,y = m.groups(); y=int(y); 
        if y<100: y+=2000
        mn=int(mn); d=int(d)
        import datetime as _dt
        if y>_dt.date.today().year: return (None,None,None)
        if 1<=mn<=12 and 1<=d<=31: return (f"{y:04d}-{mn:02d}-{d:02d}","dmy","day")
    m = re.search(r"(\d{1,2})\.\s*([A-Za-zÄÖÜäöüß\.]+)\s*(\d{4})?", s1)
    if m:
        d, mon, y = m.groups(); d=int(d); mon=mon.lower(); mn=MONTHS.get(mon)
        if mn:
            import datetime as _dt
            y = int(y) if y else _dt.date.today().year
            if y>_dt.date.today().year: return (None,None,None)
            return (f"{y:04d}-{mn:02d}-{d:02d}","d_mon_y" if y else "d_mon","day")
    m = re.search(r"\b(20\d{2}|19\d{2})\b", s1)
    if m:
        y=int(m.group(1))
        import datetime as _dt
        if y>_dt.date.today().year: return (None,None,None)
        return (f"{y:04d}-06-15","year_fallback","year")
    return (None,None,None)