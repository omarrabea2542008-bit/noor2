"""
شاشات التطبيق المختلفة
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.core.window import Window
from datetime import datetime, timedelta
from database import (
    get_last_read, save_last_read, add_tasbih, get_tasbih_count,
    get_setting, update_settings,
    set_ramadan_plan, get_ramadan_plan, add_ramadan_pages, get_ramadan_daily_target,
    get_average_reading
)
from islamic_data import ADHKAR_SABAH, ADHKAR_MASAA, DUAS, HADITH, PRAYER_NAMES, SURAHS
from khatma import update_khatma, get_khatma_pages, get_completed_khatmas
from achievements import check_achievements, unlock_badge
from hijri_utils import get_hijri_date, gregorian_to_hijri
from statistics import get_ramadan_plan_stats
import json
import os

class HomeScreen(Screen):
    """الشاشة الرئيسية"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # العنوان
        title = Label(
            text="نور - تطبيق ديني شامل",
            size_hint_y=0.1,
            font_size=28,
            bold=True
        )
        layout.add_widget(title)
        
        # شبكة الأزرار الرئيسية
        grid = GridLayout(cols=2, spacing=15, size_hint_y=0.7)
        
        buttons = [
            ("📖\nقراءة القرآن", 'quran'),
            ("🕌\nأوقات الصلاة", 'prayer'),
            ("🔔\nالأذكار", 'adhkar'),
            ("📿\nالتسبيح", 'tasbih'),
            ("🤲\nالأدعية", 'dua'),
            ("📚\nالأحاديث", 'hadith'),
            ("🌙\nخطة رمضان", 'ramadan'),
            ("📊\nالإحصائيات", 'stats'),
            ("⚙️\nالإعدادات", 'settings')
        ]
        
        for text, screen_name in buttons:
            btn = Button(
                text=text,
                size_hint=(1, 1),
                background_color=(0.2, 0.6, 0.86, 1)
            )
            btn.bind(on_press=self.go_to_screen(screen_name))
            grid.add_widget(btn)
        
        layout.add_widget(grid)
        
        # الآية اليومية
        daily_ayah = Label(
            text="بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
            size_hint_y=0.2,
            font_size=18,
            italic=True
        )
        layout.add_widget(daily_ayah)

        # التاريخ الهجري
        self.hijri_label = Label(
            text=f"التاريخ الهجري: {get_hijri_date()}",
            size_hint_y=0.05,
            font_size=16
        )
        layout.add_widget(self.hijri_label)

        # عرض الحدث الإسلامي القادم
        event_text = self.get_next_event_text()
        self.event_label = Label(text=event_text, size_hint_y=0.05, font_size=14, italic=True)
        layout.add_widget(self.event_label)

        # التاريخ الهجري
        self.hijri_label = Label(
            text=f"التاريخ الهجري: {get_hijri_date()}",
            size_hint_y=0.05,
            font_size=16
        )
        layout.add_widget(self.hijri_label)

        # تهنئة رمضانية إذا كنا في شهر رمضان
        y, m, d = gregorian_to_hijri(datetime.now())
        if m == 9:
            self.ramadan_greet = Label(
                text="رمضان كريم 🌙",
                size_hint_y=0.05,
                font_size=18,
                color=(1, 0.7, 0.2, 1)
            )
            layout.add_widget(self.ramadan_greet)
        else:
            # create empty label to maintain attribute
            self.ramadan_greet = Label(text="", size_hint_y=0.05)
            layout.add_widget(self.ramadan_greet)
        
        self.add_widget(layout)
    
    def go_to_screen(self, name):
        def callback(instance):
            self.manager.current = name
        return callback

    def on_pre_enter(self):
        # update hijri date whenever returning to home
        if hasattr(self, 'hijri_label'):
            self.hijri_label.text = f"التاريخ الهجري: {get_hijri_date()}"
        # update Ramadan greeting
        if hasattr(self, 'ramadan_greet'):
            y, m, d = gregorian_to_hijri(datetime.now())
            if m == 9:
                self.ramadan_greet.text = "رمضان كريم 🌙"
            else:
                self.ramadan_greet.text = ""
        # update next event text
        if hasattr(self, 'event_label'):
            self.event_label.text = self.get_next_event_text()

    def get_next_event_text(self):
        from islamic_data import ISLAMIC_EVENTS
        y, m, d = gregorian_to_hijri(datetime.now())
        # find event on same month/day >= today
        candidates = []
        for (em, ed), name in ISLAMIC_EVENTS.items():
            if em == m and ed >= d:
                candidates.append((em, ed, name))
        if not candidates:
            # look at next months
            for (em, ed), name in ISLAMIC_EVENTS.items():
                if em > m:
                    candidates.append((em, ed, name))
        if candidates:
            # choose earliest
            candidates.sort(key=lambda x: (x[0], x[1]))
            em, ed, name = candidates[0]
            return f"الحدث القادم: {name} ({em}/{ed})"
        return "لا توجد مناسبات قريبة"


class QuranScreen(Screen):
    """شاشة قراءة القرآن"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'quran'
        self.current_surah = 1
        self.current_ayah = 1
        self.quran_data = None
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # العنوان
        title = Label(text="📖 قراءة القرآن الكريم", size_hint_y=0.1, font_size=22, bold=True)
        layout.add_widget(title)
        
        # اختيار السورة
        surah_names = [s['name'] for s in SURAHS]
        # العرض في الـ Spinner يجب أن يكون اسم السورة فقط (القيمة تُطابق قائمة الأسماء)
        spinner = Spinner(
            text=SURAHS[0]['name'],
            values=surah_names,
            size_hint_y=0.1
        )
        spinner.bind(text=self.on_surah_selected)
        layout.add_widget(spinner)
        
        # منطقة الآيات - عرض كل الآيات في قائمة قابلة للتمرير
        scroll = ScrollView(size_hint=(1, 0.7))
        self.ayahs_layout = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.ayahs_layout.bind(minimum_height=self.ayahs_layout.setter('height'))
        scroll.add_widget(self.ayahs_layout)
        layout.add_widget(scroll)
        
        # الأزرار
        button_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        
        prev_btn = Button(text="◀ السابقة")
        prev_btn.bind(on_press=self.prev_ayah)
        button_layout.add_widget(prev_btn)

        save_btn = Button(text="💾 حفظ")
        save_btn.bind(on_press=self.save_progress)
        button_layout.add_widget(save_btn)

        next_btn = Button(text="التالية ▶")
        next_btn.bind(on_press=self.next_ayah)
        button_layout.add_widget(next_btn)
        
        layout.add_widget(button_layout)
        
        # زر العودة
        back_btn = Button(text="◀ عودة", size_hint_y=0.05)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def on_surah_selected(self, spinner, text):
        for surah in SURAHS:
            if surah['name'] == text:
                self.current_surah = surah['number']
                self.current_ayah = 1
                self.update_ayah_display()
                break
    
    def update_ayah_display(self):
        surah = next((s for s in SURAHS if s['number'] == self.current_surah), None)
        # تأكد من تحميل بيانات المصحف إذا كانت متاحة
        if self.quran_data is None:
            self.load_quran_data()

        # افرغ قائمة العرض وأعد ملئها بكل الآيات
        self.ayahs_layout.clear_widgets()
        if not surah:
            return

        # رأس السورة
        header_label = Label(
            text=f"{surah['name']} - عدد الآيات: {surah.get('ayahs', '?')}",
            size_hint_y=None,
            height=40,
            font_size=18,
            bold=True
        )
        self.ayahs_layout.add_widget(header_label)

        total = surah.get('ayahs', 0)
        for i in range(1, total + 1):
            ayah_text = None
            try:
                if self.quran_data:
                    # حاول الحصول على النص بنفس الصيغ المدعومة سابقًا
                    if isinstance(self.quran_data, dict) and 'surahs' in self.quran_data:
                        sdata = self.quran_data['surahs'].get(str(self.current_surah))
                        if sdata and 'ayahs' in sdata and len(sdata['ayahs']) >= i:
                            ayah_text = sdata['ayahs'][i - 1]
                    if ayah_text is None and isinstance(self.quran_data, dict) and str(self.current_surah) in self.quran_data:
                        arr = self.quran_data.get(str(self.current_surah))
                        if isinstance(arr, list) and len(arr) >= i:
                            ayah_text = arr[i - 1]
                    if ayah_text is None and isinstance(self.quran_data, list):
                        sindex = self.current_surah - 1
                        if 0 <= sindex < len(self.quran_data):
                            sdata = self.quran_data[sindex]
                            if isinstance(sdata, dict) and 'ayahs' in sdata and len(sdata['ayahs']) >= i:
                                ayah_text = sdata['ayahs'][i - 1]
            except Exception:
                ayah_text = None

            display = ayah_text if ayah_text else f"(نص الآية غير متوفر)"
            label = Label(
                text=f"{i}. {display}",
                size_hint_y=None,
                height=80,
                font_size=16,
                markup=True
            )
            self.ayahs_layout.add_widget(label)

    def load_quran_data(self):
        try:
            path = os.path.join(os.path.dirname(__file__), 'quran.json')
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        self.quran_data = None
                        return
                    self.quran_data = json.loads(content)
            else:
                self.quran_data = None
        except Exception:
            self.quran_data = None
    
    def prev_ayah(self, instance):
        if self.current_ayah > 1:
            self.current_ayah -= 1
            self.update_ayah_display()

    def next_ayah(self, instance):
        surah = next((s for s in SURAHS if s['number'] == self.current_surah), None)
        if surah and self.current_ayah < surah['ayahs']:
            self.current_ayah += 1
            self.update_ayah_display()
            # log a single ayah read
            from database import log_reading
            log_reading(1)
    
    def next_ayah(self, instance):
        surah = next((s for s in SURAHS if s['number'] == self.current_surah), None)
        if surah and self.current_ayah < surah['ayahs']:
            self.current_ayah += 1
            self.update_ayah_display()
    
    def save_progress(self, instance):
        surah = next((s for s in SURAHS if s['number'] == self.current_surah), None)
        if surah:
            save_last_read(surah['name'], self.current_ayah)
            self.ayah_label.text += "\n✅ تم حفظ التقدم"
            from database import log_reading
            log_reading(1)


class PrayerScreen(Screen):
    """شاشة أوقات الصلاة"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'prayer'
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(text="🕌 أوقات الصلاة", size_hint_y=0.1, font_size=22, bold=True)
        layout.add_widget(title)
        
        # قائمة الصلوات
        scroll = ScrollView()
        prayer_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        prayer_layout.bind(minimum_height=prayer_layout.setter('height'))
        
        from prayer_utils import get_today_prayer_times
        # refresh times to ensure current
        times = get_today_prayer_times()
        
        for prayer_key, prayer_name in PRAYER_NAMES.items():
            prayer_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
            
            prayer_label = Label(
                text=f"{prayer_name}",
                size_hint_x=0.6,
                font_size=18,
                bold=True
            )
            prayer_box.add_widget(prayer_label)
            
            time_label = Label(
                text=times.get(prayer_key, "لم يتحدد"),
                size_hint_x=0.4,
                font_size=18
            )
            prayer_box.add_widget(time_label)
            
            prayer_layout.add_widget(prayer_box)
        
        scroll.add_widget(prayer_layout)
        layout.add_widget(scroll)

        # زر تحديث الأوقات
        refresh_btn = Button(text="🔄 تحديث الأوقات", size_hint_y=0.1)
        refresh_btn.bind(on_press=lambda x: self.build_ui())
        layout.add_widget(refresh_btn)
        
        # زر العودة
        back_btn = Button(text="◀ عودة", size_hint_y=0.1)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)


class AdhkarScreen(Screen):
    """شاشة الأذكار"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'adhkar'
        self.current_adhkar_list = ADHKAR_SABAH
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(text="🔔 الأذكار", size_hint_y=0.1, font_size=22, bold=True)
        layout.add_widget(title)
        
        # اختيار نوع الأذكار
        button_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        
        sabah_btn = Button(text="أذكار الصباح")
        sabah_btn.bind(on_press=self.show_sabah)
        button_layout.add_widget(sabah_btn)
        
        masaa_btn = Button(text="أذكار المساء")
        masaa_btn.bind(on_press=self.show_masaa)
        button_layout.add_widget(masaa_btn)
        
        layout.add_widget(button_layout)
        
        # عرض الأذكار
        scroll = ScrollView()
        self.adhkar_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.adhkar_layout.bind(minimum_height=self.adhkar_layout.setter('height'))
        
        self.display_adhkar()
        
        scroll.add_widget(self.adhkar_layout)
        layout.add_widget(scroll)
        
        # زر العودة
        back_btn = Button(text="◀ عودة", size_hint_y=0.1)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def display_adhkar(self):
        self.adhkar_layout.clear_widgets()
        for adhkar in self.current_adhkar_list:
            adhkar_box = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=120,
                padding=10,
                spacing=5
            )
            
            text_label = Label(
                text=adhkar['text'],
                size_hint_y=0.7,
                markup=True,
                font_size=16
            )
            adhkar_box.add_widget(text_label)
            
            count_label = Label(
                text=f"العدد: {adhkar['count']}",
                size_hint_y=0.3,
                font_size=12
            )
            adhkar_box.add_widget(count_label)
            
            self.adhkar_layout.add_widget(adhkar_box)
    
    def show_sabah(self, instance):
        self.current_adhkar_list = ADHKAR_SABAH
        self.display_adhkar()
    
    def show_masaa(self, instance):
        self.current_adhkar_list = ADHKAR_MASAA
        self.display_adhkar()


class TasbihScreen(Screen):
    """شاشة التسبيح"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'tasbih'
        self.count = 0
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        title = Label(text="📿 السبحة الإلكترونية", size_hint_y=0.1, font_size=22, bold=True)
        layout.add_widget(title)
        
        # عرض العداد
        self.counter_label = Label(
            text=str(self.count),
            size_hint_y=0.3,
            font_size=80,
            bold=True
        )
        layout.add_widget(self.counter_label)
        
        # الذكر
        dhikr_label = Label(
            text="سُبْحَانَ اللَّهِ\nالْحَمْدُ لِلَّهِ\nلَا إِلَهَ إِلَّا اللَّهُ\nاللَّهُ أَكْبَرُ",
            size_hint_y=0.2,
            font_size=18,
            markup=True
        )
        layout.add_widget(dhikr_label)
        
        # أزرار التحكم
        button_layout = BoxLayout(size_hint_y=0.25, spacing=10)
        
        plus_btn = Button(text="+", font_size=40)
        plus_btn.bind(on_press=self.increment)
        button_layout.add_widget(plus_btn)
        
        reset_btn = Button(text="إعادة تعيين")
        reset_btn.bind(on_press=self.reset)
        button_layout.add_widget(reset_btn)
        
        save_btn = Button(text="💾 حفظ")
        save_btn.bind(on_press=self.save)
        button_layout.add_widget(save_btn)
        
        layout.add_widget(button_layout)
        
        # زر العودة
        back_btn = Button(text="◀ عودة", size_hint_y=0.1)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def increment(self, instance):
        self.count += 1
        self.counter_label.text = str(self.count)
    
    def reset(self, instance):
        self.count = 0
        self.counter_label.text = "0"
    
    def save(self, instance):
        add_tasbih(self.count)
        self.counter_label.text = "✅ تم الحفظ"


class DuaScreen(Screen):
    """شاشة الأدعية"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'dua'
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(text="🤲 الأدعية", size_hint_y=0.1, font_size=22, bold=True)
        layout.add_widget(title)
        
        # قائمة الأدعية
        scroll = ScrollView()
        dua_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        dua_layout.bind(minimum_height=dua_layout.setter('height'))
        
        for dua in DUAS:
            dua_box = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=100,
                padding=10,
                spacing=5
            )
            
            title_label = Label(
                text=dua['title'],
                size_hint_y=0.3,
                font_size=16,
                bold=True
            )
            dua_box.add_widget(title_label)
            
            text_label = Label(
                text=dua['text'],
                size_hint_y=0.7,
                font_size=14,
                markup=True
            )
            dua_box.add_widget(text_label)
            
            dua_layout.add_widget(dua_box)
        
        scroll.add_widget(dua_layout)
        layout.add_widget(scroll)
        
        # زر العودة
        back_btn = Button(text="◀ عودة", size_hint_y=0.1)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)


class HadithScreen(Screen):
    """شاشة الأحاديث"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'hadith'
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(text="📚 الأحاديث الشريفة", size_hint_y=0.1, font_size=22, bold=True)
        layout.add_widget(title)
        
        # قائمة الأحاديث
        scroll = ScrollView()
        hadith_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        hadith_layout.bind(minimum_height=hadith_layout.setter('height'))
        
        for hadith in HADITH:
            hadith_box = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=140,
                padding=10,
                spacing=5
            )
            
            text_label = Label(
                text=hadith['text'],
                size_hint_y=0.7,
                font_size=13,
                markup=True
            )
            hadith_box.add_widget(text_label)
            
            source_label = Label(
                text=f"المصدر: {hadith['source']}",
                size_hint_y=0.3,
                font_size=11,
                italic=True
            )
            hadith_box.add_widget(source_label)
            
            hadith_layout.add_widget(hadith_box)
        
        scroll.add_widget(hadith_layout)
        layout.add_widget(scroll)
        
        # زر العودة
        back_btn = Button(text="◀ عودة", size_hint_y=0.1)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)


class StatisticsScreen(Screen):
    """شاشة الإحصائيات"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'stats'
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(text="📊 الإحصائيات", size_hint_y=0.1, font_size=22, bold=True)
        layout.add_widget(title)
        
        # الإحصائيات
        stats_layout = GridLayout(cols=2, spacing=20, size_hint_y=0.7)
        
        # نجلب البيانات الحيّة
        stats = []
        stats.append(("عدد التسبيحات اليوم", str(get_tasbih_count())))
        stats.append(("الختمات المكتملة", str(get_completed_khatmas())))
        # خطط القراءة
        plan = get_ramadan_plan()
        if plan:
            total = 604
            pages = plan['pages_read']
            stats.append(("خطة رمضان", f"{pages}/{total} صفحة"))
        else:
            stats.append(("خطة رمضان", "لا توجد"))
        
        # إحصائيات قراءة إضافية
        avg = get_average_reading(7)
        stats.append(("متوسط القراءة 7 أيام", f"{avg:.1f} صفحة"))
        # إضافة متوسط الخطة إن وجد
        plan_stats = get_ramadan_plan_stats()
        if plan_stats:
            stats.append(("متوسط خطة رمضان", f"{plan_stats['avg_per_day']:.1f} صفحة/يوم"))
        
        for label_text, value in stats:
            stat_box = BoxLayout(orientation='vertical', padding=10, spacing=5)
            
            label = Label(
                text=label_text,
                size_hint_y=0.4,
                font_size=14,
                bold=True
            )
            stat_box.add_widget(label)
            
            value_label = Label(
                text=value,
                size_hint_y=0.6,
                font_size=28,
                bold=True,
                color=(0.2, 0.6, 0.86, 1)
            )
            stat_box.add_widget(value_label)
            
            stats_layout.add_widget(stat_box)
        
        layout.add_widget(stats_layout)
        
        # زر العودة
        back_btn = Button(text="◀ عودة", size_hint_y=0.2)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)


class RamadanPlanScreen(Screen):
    """شاشة خطة رمضان (ختمة القرآن خلال رمضان)"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'ramadan'
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        title = Label(text="🌙 خطة رمضان", size_hint_y=0.1, font_size=22, bold=True)
        layout.add_widget(title)

        # معلومات الخطة الحالية
        self.info_label = Label(text="", size_hint_y=0.2, font_size=16)
        layout.add_widget(self.info_label)
        self.update_plan_info()

        # أزرار اختيار الخطة
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        for days in [10, 15, 20]:
            b = Button(text=f"ختمة {days} يوم")
            b.bind(on_press=self.choose_plan(days))
            btn_layout.add_widget(b)
        layout.add_widget(btn_layout)

        # زر إضافة صفحات
        add_btn = Button(text="📄 تسجيل صفحات مقروءة")
        add_btn.bind(on_press=self.add_pages)
        layout.add_widget(add_btn)

        # زر عرض تقويم رمضان
        cal_btn = Button(text="📆 عرض تقويم رمضان")
        cal_btn.bind(on_press=self.show_calendar)
        layout.add_widget(cal_btn)

        # زر العودة
        back = Button(text="◀ عودة", size_hint_y=0.1)
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back)

        self.add_widget(layout)

    def update_plan_info(self):
        plan = get_ramadan_plan()
        if plan:
            target = get_ramadan_daily_target() or '?'
            total = 604
            remaining = total - plan['pages_read']
            self.info_label.text = (f"الخطة الحالية: {plan['plan_days']} يوم\n"
                                    f"بدءاً من {plan['start_date']}\n"
                                    f"الصفحات المقروءة: {plan['pages_read']} من {total}\n"
                                    f"الصفحات المطلوبة يومياً: {target}\n"
                                    f"المتبقي: {remaining}")
        else:
            self.info_label.text = "لم يتم اختيار خطة بعد."

    def choose_plan(self, days):
        def callback(instance):
            set_ramadan_plan(days)
            self.update_plan_info()
        return callback

    def get_ramadan_calendar(self):
        plan = get_ramadan_plan()
        if not plan:
            return []
        start = datetime.strptime(plan['start_date'], "%Y-%m-%d")
        days = plan['plan_days']
        from prayer_utils import fetch_prayer_times, get_location
        lat, lon = get_location()
        cal = []
        for i in range(days):
            date = start + timedelta(days=i)
            if lat is not None and lon is not None:
                times = fetch_prayer_times(lat, lon, date.strftime("%Y-%m-%d"))
            else:
                times = {}
            suhur = times.get('fajr', '')
            iftar = times.get('maghrib', '')
            cal.append((date.strftime("%Y-%m-%d"), suhur, iftar))
        return cal

    def show_calendar(self, instance):
        cal = self.get_ramadan_calendar()
        if not cal:
            # try full Ramadan month
            from hijri_utils import get_ramadan_gregorian_dates
            dates = get_ramadan_gregorian_dates()
            if not dates:
                popup = Popup(title="تقويم رمضان", content=Label(text="لا توجد خطة لتوليد التقويم ولا يمكن تحديد رمضان"), size_hint=(0.8, 0.4))
                popup.open()
                return
            # build cal list from dates
            from prayer_utils import fetch_prayer_times, get_location
            lat, lon = get_location()
            cal = []
            for date in dates:
                if lat is not None and lon is not None:
                    times = fetch_prayer_times(lat, lon, date)
                else:
                    times = {}
                cal.append((date, times.get('fajr',''), times.get('maghrib','')))
        # build display
        scroll = ScrollView(size_hint=(1, 0.8))
        grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        for date, suhur, iftar in cal:
            lbl = Label(text=f"{date} - سحور: {suhur} - إفطار: {iftar}", size_hint_y=None, height=40, font_size=14)
            grid.add_widget(lbl)
        scroll.add_widget(grid)
        content = BoxLayout(orientation='vertical')
        content.add_widget(scroll)
        btn = Button(text="إغلاق", size_hint_y=0.1)
        popup = Popup(title="تقويم رمضان", content=content, size_hint=(0.9, 0.9))
        btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(btn)
        popup.open()

    def add_pages(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        ti = TextInput(hint_text="عدد الصفحات", input_filter='int', multiline=False)
        btn = Button(text="تأكيد", size_hint_y=0.3)
        content.add_widget(ti)
        content.add_widget(btn)
        popup = Popup(title="إضافة صفحات", content=content, size_hint=(0.8, 0.4))
        def on_confirm(_):
            try:
                pages = int(ti.text)
            except:
                pages = 0
            if pages > 0:
                new = add_ramadan_pages(pages)
                update_khatma(pages)
                self.update_plan_info()
                # notify if passed today's target
                target = get_ramadan_daily_target()
                if target and new >= target:
                    from notifications import send_notification
                    send_notification("✅ هدف اليوم", "لقد وصلت أو تخطيت هدفك اليومي!", timeout=10)
                if new and new >= 604:
                    unlock_badge("ختمة رمضان")
                popup.dismiss()
        btn.bind(on_press=on_confirm)
        popup.open()

    # end of RamadanPlanScreen, build_ui already defined above


class SettingsScreen(Screen):
    """شاشة الإعدادات"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = Label(text="⚙️ الإعدادات", size_hint_y=0.1, font_size=22, bold=True)
        layout.add_widget(title)
        
        # خيارات الإعدادات
        settings_layout = GridLayout(cols=1, spacing=10, size_hint_y=0.6)
        
        # الوضع الليلي
        dark_mode_layout = BoxLayout(size_hint_y=0.2)
        dark_mode_label = Label(text="الوضع الليلي", size_hint_x=0.7)
        dark_mode_btn = Button(text="تفعيل", size_hint_x=0.3)
        dark_mode_btn.bind(on_press=self.toggle_dark_mode)
        dark_mode_layout.add_widget(dark_mode_label)
        dark_mode_layout.add_widget(dark_mode_btn)
        settings_layout.add_widget(dark_mode_layout)
        
        # التنبيهات
        notification_layout = BoxLayout(size_hint_y=0.2)
        notification_label = Label(text="التنبيهات", size_hint_x=0.7)
        notification_btn = Button(text="تفعيل", size_hint_x=0.3)
        notification_layout.add_widget(notification_label)
        notification_layout.add_widget(notification_btn)
        settings_layout.add_widget(notification_layout)

        # الموقع الجغرافي
        loc_layout = BoxLayout(size_hint_y=0.2, spacing=5)
        loc_label = Label(text="إحداثيات الموقع", size_hint_x=0.4)
        self.lat_input = TextInput(hint_text="خط العرض", input_filter='float', size_hint_x=0.3, multiline=False)
        self.lon_input = TextInput(hint_text="خط الطول", input_filter='float', size_hint_x=0.3, multiline=False)
        loc_layout.add_widget(loc_label)
        loc_layout.add_widget(self.lat_input)
        loc_layout.add_widget(self.lon_input)
        settings_layout.add_widget(loc_layout)

        # زر حفظ الموقع وتحديث أوقات الصلاة
        loc_btn = Button(text="حفظ الموقع وتحديث أوقات الصلاة")
        loc_btn.bind(on_press=self.save_location)
        settings_layout.add_widget(loc_btn)
        
        # حجم الخط
        font_layout = BoxLayout(size_hint_y=0.2)
        font_label = Label(text="حجم الخط", size_hint_x=0.7)
        font_spinner = Spinner(
            text="متوسط",
            values=["صغير", "متوسط", "كبير"],
            size_hint_x=0.3
        )
        font_layout.add_widget(font_label)
        font_layout.add_widget(font_spinner)
        settings_layout.add_widget(font_layout)
        
        layout.add_widget(settings_layout)
        
        # زر العودة
        back_btn = Button(text="◀ عودة", size_hint_y=0.2)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def toggle_dark_mode(self, instance):
        current = get_setting("dark_mode", "true")
        new_value = "false" if current == "true" else "true"
        update_settings("dark_mode", new_value)
        instance.text = "تعطيل" if new_value == "true" else "تفعيل"

    def on_pre_enter(self):
        # populate location fields if stored
        from prayer_utils import get_location
        lat, lon = get_location()
        if lat is not None:
            self.lat_input.text = str(lat)
        if lon is not None:
            self.lon_input.text = str(lon)

    def save_location(self, instance):
        from prayer_utils import set_location, refresh_prayer_times
        try:
            lat = float(self.lat_input.text)
            lon = float(self.lon_input.text)
            set_location(lat, lon)
            # immediately refresh global prayer times
            refresh_prayer_times()
            send = "🗺️ تم حفظ الموقع وتحديث أوقات الصلاة"
        except Exception as e:
            send = f"خطأ في حفظ الموقع: {e}"
        popup = Popup(title="حفظ الموقع", content=Label(text=send), size_hint=(0.6, 0.3))
        popup.open()
