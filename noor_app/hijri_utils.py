from datetime import datetime


def gregorian_to_hijri(g_date: datetime):
    """Convert a Gregorian date to Hijri (Islamic) date using civil algorithm.
    Returns a tuple (year, month, day).
    Algorithm adopted from the Umm al-Qura / civil conversion.
    """
    # based on algorithm from https://en.wikipedia.org/wiki/Tabular_Islamic_calendar
    # this function works for years in a reasonable modern range
    day = g_date.day
    month = g_date.month
    year = g_date.year

    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    # Julian day
    jd = day + ((153 * m + 2) // 5) + 365 * y + y // 4 - y // 100 + y // 400 - 32045

    # Islamic date
    l = jd - 1948440 + 10632
    n = (l - 1) // 10631
    l = l - 10631 * n + 354
    j = ((10985 - l) // 5316) * ((50 * l) // 17719) + (l // 5670) * ((43 * l) // 15238)
    l = l - ((30 - j) // 15) * ((17719 * j) // 50) - (j // 16) * ((15238 * j) // 43) + 29
    m = (24 * l) // 709
    d = l - (709 * m) // 24
    y = 30 * n + j - 30
    return int(y), int(m), int(d)


def get_hijri_date():
    """Return formatted hijri date string like '1447/06/09'."""
    today = datetime.now()
    y, m, d = gregorian_to_hijri(today)
    return f"{y}/{m:02d}/{d:02d}"


def get_ramadan_gregorian_dates():
    """Return list of gregorian dates (YYYY-MM-DD) that correspond to Ramadan of the current hijri year.
    Uses incremental search via conversion; may be off by a day depending on lunar sighting but gives reasonable approximation.
    """
    from datetime import timedelta
    date = datetime.now()
    start = None
    # search backwards up to a year to find 1st of Ramadan
    for i in range(370):
        y, m, d = gregorian_to_hijri(date)
        if m == 9 and d == 1:
            start = date
            break
        date -= timedelta(days=1)
    if not start:
        return []
    # collect days until month changes
    result = []
    cur = start
    while True:
        y, m, d = gregorian_to_hijri(cur)
        if m != 9:
            break
        result.append(cur.strftime("%Y-%m-%d"))
        cur += timedelta(days=1)
    return result
