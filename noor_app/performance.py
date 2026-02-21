"""
تحسينات الأداء والمراقبة
"""

import gc
import logging
from kivy.logger import Logger
from datetime import datetime


# إعداد نظام السجلات
logging.basicConfig(
    filename='noor.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('NoorApp')


class PerformanceMonitor:
    """مراقب الأداء"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.memory_usage = 0
    
    def log_event(self, event_name):
        """تسجيل حدث معين"""
        logger.info(f"Event: {event_name}")
    
    def log_error(self, error_message):
        """تسجيل خطأ"""
        logger.error(f"Error: {error_message}")
    
    def optimize_memory(self):
        """تحسين استخدام الذاكرة"""
        gc.collect()
        logger.info("Memory optimized")
    
    def get_app_uptime(self):
        """الحصول على مدة تشغيل التطبيق"""
        uptime = datetime.now() - self.start_time
        return uptime


# مثيل المراقب
performance = PerformanceMonitor()


def log_screen_navigation(screen_name):
    """تسجيل تنقل المستخدم بين الشاشات"""
    performance.log_event(f"Navigated to {screen_name}")


def log_user_action(action_name, details=""):
    """تسجيل تصرف المستخدم"""
    message = f"User action: {action_name}"
    if details:
        message += f" - {details}"
    performance.log_event(message)


def handle_exception(exception, context=""):
    """التعامل مع الاستثناءات"""
    error_msg = f"Exception in {context}: {str(exception)}"
    performance.log_error(error_msg)
    Logger.exception(error_msg)


class CacheManager:
    """مدير التخزين المؤقت"""
    
    def __init__(self):
        self.cache = {}
    
    def get(self, key, default=None):
        """الحصول على قيمة من التخزين المؤقت"""
        return self.cache.get(key, default)
    
    def set(self, key, value):
        """حفظ قيمة في التخزين المؤقت"""
        self.cache[key] = value
    
    def clear(self):
        """مسح التخزين المؤقت"""
        self.cache.clear()


cache_manager = CacheManager()
