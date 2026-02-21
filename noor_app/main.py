"""
تطبيق نور - تطبيق ديني إسلامي شامل
يتضمن: قراءة القرآن، الأذكار، التسبيح، الأدعية، الأحاديث، أوقات الصلاة، الإحصائيات
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
import json
from datetime import datetime

from database import get_setting, update_settings
from screens import (
    HomeScreen, QuranScreen, PrayerScreen, AdhkarScreen,
    TasbihScreen, DuaScreen, HadithScreen, StatisticsScreen, RamadanPlanScreen, SettingsScreen
)

# إعدادات النافذة
Window.size = (400, 800)
Window.left = 0
Window.top = 0


class NoorApp(App):
    """التطبيق الرئيسي"""
    
    def build(self):
        self.load_theme()
        
        # إنشاء مدير الشاشات
        self.screen_manager = ScreenManager()
        
        # اضبط أوقات الصلاة عند البداية
        try:
            from prayer_utils import refresh_prayer_times
            refresh_prayer_times()
        except:
            pass
        
        # إضافة الشاشات
        self.screen_manager.add_widget(HomeScreen())
        self.screen_manager.add_widget(QuranScreen())
        self.screen_manager.add_widget(PrayerScreen())
        self.screen_manager.add_widget(AdhkarScreen())
        self.screen_manager.add_widget(TasbihScreen())
        self.screen_manager.add_widget(DuaScreen())
        self.screen_manager.add_widget(HadithScreen())
        self.screen_manager.add_widget(StatisticsScreen())
        self.screen_manager.add_widget(RamadanPlanScreen())
        self.screen_manager.add_widget(SettingsScreen())
        
        return self.screen_manager
    
    def load_theme(self):
        """تحميل وتطبيق المظهر"""
        try:
            dark_mode = get_setting("dark_mode", "true") == "true"
            if dark_mode:
                # وضع مظلم
                Window.clearcolor = (0.1, 0.1, 0.15, 1)
            else:
                # وضع فاتح
                Window.clearcolor = (0.95, 0.95, 0.98, 1)
        except:
            Window.clearcolor = (0.1, 0.1, 0.15, 1)
    
    def on_pause(self):
        """عند تعليق التطبيق"""
        return True
    
    def on_start(self):
        """عند بدء التطبيق"""
        try:
            from notifications import start_notifications
            start_notifications()
        except Exception as e:
            print("failed to start notifications", e)

    def on_resume(self):
        """عند استئناف التطبيق"""
        self.load_theme()


if __name__ == "__main__":
    NoorApp().run()
