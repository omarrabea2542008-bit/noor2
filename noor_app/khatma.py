import sqlite3

conn = sqlite3.connect("noor.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS khatma (
    pages INTEGER,
    completed INTEGER DEFAULT 0
)
""")

def update_khatma(pages):
    """إضافة صفحات للختمة"""
    c.execute("SELECT pages FROM khatma")
    row = c.fetchone()

    if row:
        new_pages = row[0] + pages
        if new_pages >= 604:
            print("تمت الختمة 🎉")
            increment_completed()
            new_pages = 0
        c.execute("UPDATE khatma SET pages=?", (new_pages,))
    else:
        c.execute("INSERT INTO khatma VALUES (?, 0)", (pages,))

    conn.commit()

def get_khatma_pages():
    """الحصول على عدد الصفحات المقروءة"""
    c.execute("SELECT pages FROM khatma")
    row = c.fetchone()
    return row[0] if row else 0

def get_completed_khatmas():
    """الحصول على عدد الختمات المكتملة"""
    c.execute("SELECT completed FROM khatma LIMIT 1")
    row = c.fetchone()
    return row[0] if row else 0

def increment_completed():
    """إضافة 1 للختمات المكتملة"""
    c.execute("UPDATE khatma SET completed = completed + 1")
    conn.commit()

conn.commit()