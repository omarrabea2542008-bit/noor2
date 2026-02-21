import sqlite3
from datetime import datetime

conn = sqlite3.connect("noor.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    date DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    badge_name TEXT UNIQUE,
    unlocked_date DATETIME
)
""")

conn.commit()

def check_achievements():
    """التحقق من الإنجازات الجديدة"""
    from database import get_ramadan_plan, get_reading_pages
    
    # الإنجاز الأول: بدء الختمة
    c.execute("SELECT * FROM achievements WHERE name = 'أول خطوة في الختمة'")
    if not c.fetchone():
        c.execute("INSERT INTO achievements (name) VALUES (?)", ("أول خطوة في الختمة",))
        conn.commit()
    # بداية خطة رمضان
    plan = get_ramadan_plan()
    if plan:
        c.execute("SELECT * FROM achievements WHERE name = 'بدأت خطة رمضان'")
        if not c.fetchone():
            c.execute("INSERT INTO achievements (name) VALUES (?)", ("بدأت خطة رمضان",))
            conn.commit()
    # أول تسجيل قراءة
    pages = get_reading_pages(datetime.now().strftime("%Y-%m-%d"))
    if pages > 0:
        c.execute("SELECT * FROM achievements WHERE name = 'سجلت قراءتك الأولى'")
        if not c.fetchone():
            c.execute("INSERT INTO achievements (name) VALUES (?)", ("سجلت قراءتك الأولى",))
            conn.commit()

def unlock_badge(badge_name):
    """فتح شارة جديدة"""
    try:
        c.execute("INSERT INTO badges (badge_name, unlocked_date) VALUES (?, ?)", 
                  (badge_name, datetime.now()))
        conn.commit()
        return True
    except:
        return False

def get_achievements():
    """الحصول على جميع الإنجازات"""
    c.execute("SELECT name, date FROM achievements ORDER BY date DESC")
    return c.fetchall()

def get_badges():
    """الحصول على جميع الشارات المفتوحة"""
    c.execute("SELECT badge_name, unlocked_date FROM badges ORDER BY unlocked_date DESC")
    return c.fetchall()

def get_achievement_count():
    """الحصول على عدد الإنجازات"""
    c.execute("SELECT COUNT(*) FROM achievements")
    return c.fetchone()[0]