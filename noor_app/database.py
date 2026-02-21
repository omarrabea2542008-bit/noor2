import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("noor.db")
c = conn.cursor()

# جدول آخر قراءة
c.execute("""
CREATE TABLE IF NOT EXISTS last_read (
    surah TEXT,
    ayah INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# جدول التسبيح اليومي
c.execute("""
CREATE TABLE IF NOT EXISTS tasbih (
    date DATE,
    count INTEGER,
    PRIMARY KEY(date)
)
""")

# جدول الأذكار المقروءة
c.execute("""
CREATE TABLE IF NOT EXISTS adhkar_read (
    adhkar_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# جدول الأدعية المحفوظة
c.execute("""
CREATE TABLE IF NOT EXISTS saved_dua (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dua_text TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# جدول سجل القراءة (صفحات/آيات يومية)
c.execute("""
CREATE TABLE IF NOT EXISTS reading_log (
    date DATE PRIMARY KEY,
    pages INTEGER
)
""")

# جدول الإحصائيات
c.execute("""
CREATE TABLE IF NOT EXISTS statistics (
    date DATE,
    ayahs_read INTEGER,
    adhkar_count INTEGER,
    khatma_count INTEGER,
    PRIMARY KEY(date)
)
""")

# جدول خطة رمضان
c.execute("""
CREATE TABLE IF NOT EXISTS ramadan_plan (
    plan_days INTEGER,
    start_date DATE,
    pages_read INTEGER DEFAULT 0
)
""")

# جدول الإعدادات
c.execute("""
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

conn.commit()

def save_last_read(surah, ayah):
    c.execute("DELETE FROM last_read")
    c.execute("INSERT INTO last_read (surah, ayah) VALUES (?, ?)", (surah, ayah))
    conn.commit()

def get_last_read():
    c.execute("SELECT surah, ayah FROM last_read LIMIT 1")
    result = c.fetchone()
    return result if result else ("الفاتحة", 1)

def add_tasbih(count=1):
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT count FROM tasbih WHERE date = ?", (today,))
    row = c.fetchone()
    
    if row:
        new_count = row[0] + count
        c.execute("UPDATE tasbih SET count = ? WHERE date = ?", (new_count, today))
    else:
        c.execute("INSERT INTO tasbih (date, count) VALUES (?, ?)", (today, count))
    conn.commit()
    return get_tasbih_count()

def get_tasbih_count():
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT count FROM tasbih WHERE date = ?", (today,))
    row = c.fetchone()
    return row[0] if row else 0

def update_settings(key, value):
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    if c.fetchone():
        c.execute("UPDATE settings SET value = ? WHERE key = ?", (value, key))
    else:
        c.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()

def get_setting(key, default=""):
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    return row[0] if row else default

def get_statistics():
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT * FROM statistics WHERE date = ?", (today,))
    return c.fetchone()


def log_reading(pages):
    """Log number of pages/ayahs read for today."""
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT pages FROM reading_log WHERE date = ?", (today,))
    row = c.fetchone()
    if row:
        new_count = row[0] + pages
        c.execute("UPDATE reading_log SET pages = ? WHERE date = ?", (new_count, today))
    else:
        c.execute("INSERT INTO reading_log (date, pages) VALUES (?, ?)", (today, pages))
    conn.commit()
    return get_reading_pages(today)


def get_reading_pages(date):
    c.execute("SELECT pages FROM reading_log WHERE date = ?", (date,))
    row = c.fetchone()
    return row[0] if row else 0


def get_average_reading(days=7):
    """Return average pages read per day over past given days."""
    start = (datetime.now() - timedelta(days=days-1)).strftime("%Y-%m-%d")
    c.execute("SELECT AVG(pages) FROM reading_log WHERE date >= ?", (start,))
    row = c.fetchone()
    return row[0] if row and row[0] is not None else 0


# Ramadan plan helpers

def set_ramadan_plan(days):
    """Start a new Ramadan reading plan with the given number of days."""
    today = datetime.now().strftime("%Y-%m-%d")
    # only one plan at a time
    c.execute("DELETE FROM ramadan_plan")
    c.execute("INSERT INTO ramadan_plan (plan_days, start_date, pages_read) VALUES (?, ?, 0)",
              (days, today))
    conn.commit()


def get_ramadan_plan():
    """Return current plan as dict or None."""
    c.execute("SELECT plan_days, start_date, pages_read FROM ramadan_plan LIMIT 1")
    row = c.fetchone()
    if row:
        return {"plan_days": row[0], "start_date": row[1], "pages_read": row[2]}
    return None


def add_ramadan_pages(pages=1):
    """Record pages read for Ramadan plan and return updated count.
    Also logs reading in daily log and returns None if no active plan.
    """
    plan = get_ramadan_plan()
    if not plan:
        return None
    new_total = plan["pages_read"] + pages
    c.execute("UPDATE ramadan_plan SET pages_read = ?", (new_total,))
    conn.commit()
    # also log in reading log for deeper stats
    log_reading(pages)
    return new_total


def get_ramadan_daily_target():
    plan = get_ramadan_plan()
    if not plan or plan["plan_days"] <= 0:
        return None
    total_pages = 604
    # integer ceiling division
    return (total_pages + plan["plan_days"] - 1) // plan["plan_days"]
