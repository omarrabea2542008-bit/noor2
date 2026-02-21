"""
نظام الإحصائيات والتقارير
"""

from database import conn, c
from datetime import datetime, timedelta
import json


def record_daily_activity(ayahs_read=0, adhkar_count=0, khatma_count=0):
    """تسجيل نشاط اليوم"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    c.execute("SELECT * FROM statistics WHERE date = ?", (today,))
    if c.fetchone():
        c.execute("""
            UPDATE statistics 
            SET ayahs_read = ?, adhkar_count = ?, khatma_count = ?
            WHERE date = ?
        """, (ayahs_read, adhkar_count, khatma_count, today))
    else:
        c.execute("""
            INSERT INTO statistics (date, ayahs_read, adhkar_count, khatma_count)
            VALUES (?, ?, ?, ?)
        """, (today, ayahs_read, adhkar_count, khatma_count))
    
    conn.commit()


def get_daily_stats(date=None):
    """الحصول على إحصائيات يوم معين"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    c.execute("SELECT * FROM statistics WHERE date = ?", (date,))
    result = c.fetchone()
    
    if result:
        return {
            "date": result[0],
            "ayahs_read": result[1],
            "adhkar_count": result[2],
            "khatma_count": result[3]
        }
    return None


def get_weekly_stats():
    """الحصول على إحصائيات الأسبوع"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    c.execute("""
        SELECT date, SUM(ayahs_read), SUM(adhkar_count), SUM(khatma_count)
        FROM statistics
        WHERE date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date DESC
    """, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
    
    return c.fetchall()


def get_monthly_stats():
    """الحصول على إحصائيات الشهر"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    c.execute("""
        SELECT strftime('%Y-%m', date), 
               SUM(ayahs_read), 
               SUM(adhkar_count), 
               SUM(khatma_count)
        FROM statistics
        WHERE date BETWEEN ? AND ?
        GROUP BY strftime('%Y-%m', date)
    """, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
    
    return c.fetchall()


def get_total_stats():
    """الحصول على الإحصائيات الكلية"""
    c.execute("""
        SELECT COUNT(DISTINCT date), 
               SUM(ayahs_read), 
               SUM(adhkar_count), 
               SUM(khatma_count)
        FROM statistics
    """)
    
    result = c.fetchone()
    if result:
        return {
            "days_active": result[0] or 0,
            "total_ayahs": result[1] or 0,
            "total_adhkar": result[2] or 0,
            "total_khatmas": result[3] or 0
        }
    return {
        "days_active": 0,
        "total_ayahs": 0,
        "total_adhkar": 0,
        "total_khatmas": 0
    }


def get_streak():
    """حساب السلسلة اليومية (كم يوم متتالي نشط)"""
    c.execute("""
        SELECT date FROM statistics 
        ORDER BY date DESC
    """)
    
    dates = c.fetchall()
    if not dates:
        return 0
    
    streak = 0
    current_date = datetime.now().date()
    
    for date_tuple in dates:
        date_obj = datetime.strptime(date_tuple[0], "%Y-%m-%d").date()
        if current_date - timedelta(days=streak) == date_obj:
            streak += 1
        else:
            break
    
    return streak


def get_ramadan_plan_stats():
    """Return simple statistics about the current Ramadan plan."""
    from database import get_ramadan_plan
    plan = get_ramadan_plan()
    if not plan:
        return None
    days = plan['plan_days']
    pages = plan['pages_read']
    avg = pages / days if days else 0
    return {'plan_days': days, 'pages_read': pages, 'avg_per_day': avg}


def get_progress_percentage():
    """حساب نسبة التقدم في الختمة"""
    from khatma import get_khatma_pages
    
    pages = get_khatma_pages()
    total_pages = 604  # عدد صفحات القرآن الكريم
    
    percentage = (pages / total_pages) * 100
    return round(percentage, 2)


def export_stats_json():
    """تصدير الإحصائيات كـ JSON"""
    stats = {
        "total": get_total_stats(),
        "daily": get_daily_stats(),
        "streak": get_streak(),
        "progress": get_progress_percentage()
    }
    
    return json.dumps(stats, ensure_ascii=False, indent=2)


def clear_old_stats(days=90):
    """حذف الإحصائيات القديمة (أكثر من X يوم)"""
    old_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    c.execute("DELETE FROM statistics WHERE date < ?", (old_date,))
    conn.commit()
