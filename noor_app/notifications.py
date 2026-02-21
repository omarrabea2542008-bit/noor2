"""
نظام التنبيهات والإشعارات
"""

from kivy.support import install_gobject_iteration
from plyer import notification
from kivy.clock import Clock
from datetime import datetime, time
import threading

# إنشاء إشعارات
try:
    install_gobject_iteration()
except:
    pass


def send_notification(title, message, timeout=5):
    """إرسال إشعار للمستخدم"""
    try:
        notification.notify(
            title=title,
            message=message,
            timeout=timeout
        )
    except Exception as e:
        print(f"خطأ في الإشعار: {e}")


def setup_prayer_notifications():
    """إعداد إشعارات أوقات الصلاة"""
    from islamic_data import PRAYER_NAMES
    from prayer_utils import get_today_prayer_times, refresh_prayer_times
    
    def check_prayer_times():
        # ensure we have up-to-date times
        refresh_prayer_times()
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        times = get_today_prayer_times()
        for prayer_key, prayer_time in times.items():
            # ignore timezone offset strings etc.
            if current_time == prayer_time[:5]:
                prayer_name = PRAYER_NAMES.get(prayer_key, prayer_key)
                send_notification(
                    title=f"⏰ حان وقت {prayer_name}",
                    message=f"الوقت: {prayer_time}",
                    timeout=30
                )
    
    # تشغيل الفحص كل دقيقة
    Clock.schedule_interval(lambda dt: check_prayer_times(), 60)


def setup_adhkar_notifications():
    """إعداد إشعارات الأذكار اليومية"""
    
    def morning_notification(dt):
        send_notification(
            title="🌅 صباح الخير",
            message="لا تنسَ أذكار الصباح",
            timeout=10
        )
    
    def evening_notification(dt):
        send_notification(
            title="🌙 مساء الخير",
            message="حان وقت أذكار المساء",
            timeout=10
        )
    
    # جدولة الإشعارات (في الصباح والمساء)
    # يمكن تخصيص الأوقات حسب الحاجة
    morning_time = Clock.create_trigger(morning_notification, 1)
    evening_time = Clock.create_trigger(evening_notification, 1)


def schedule_daily_inspiration():
    """جدولة رسالة يومية قد تكون آية أو حديث أو دعاء"""
    from islamic_data import HADITH, DUAS, QURAN_VERSES
    import random
    
    def show_daily(dt):
        choice = random.choice(['verse', 'hadith', 'dua'])
        if choice == 'verse':
            text = random.choice(QURAN_VERSES)
            title = "📖 آية قرآنية"
        elif choice == 'hadith':
            hadith = random.choice(HADITH)
            text = hadith['text']
            title = "📚 الحديث الشريف"
        else:
            dua = random.choice(DUAS)
            text = dua['text']
            title = "🤲 دعاء يومي"
        send_notification(
            title=title,
            message=text[:100] + "...",
            timeout=15
        )
        # during Ramadan also send encouragement
        from hijri_utils import gregorian_to_hijri
        from islamic_data import ISLAMIC_EVENTS
        y, m, d = gregorian_to_hijri(datetime.now())
        if m == 9:
            send_notification(title="🌙 رمضان", message="حافظ على خُتمتك اليوم!", timeout=10)
        # if today is an Islamic event, notify
        if (m, d) in ISLAMIC_EVENTS:
            send_notification(title="📅 مناسبة", message=ISLAMIC_EVENTS[(m, d)], timeout=15)
    
    # تشغيل مرة واحدة يومياً
    Clock.schedule_once(show_daily, 1)


def reminder_notification(title, message):
    """إشعار تذكيري عام"""
    send_notification(title, message, timeout=10)


# بدء التنبيهات عند بدء التطبيق
def start_notifications():
    """بدء جميع نظام التنبيهات"""
    try:
        setup_prayer_notifications()
        setup_adhkar_notifications()
        schedule_daily_inspiration()
    except Exception as e:
        print(f"خطأ في بدء التنبيهات: {e}")
