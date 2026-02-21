import sys
sys.path.append(r'e:\noor_app')
from hijri_utils import get_hijri_date, get_ramadan_gregorian_dates
from database import get_ramadan_plan
from prayer_utils import set_location, get_today_prayer_times
from islamic_data import ISLAMIC_EVENTS

print('hijri', get_hijri_date())
print('plan', get_ramadan_plan())
print('ramadan dates', get_ramadan_gregorian_dates()[:3])
set_location(21.4,39.8)
print('prayers', get_today_prayer_times())
print('events', ISLAMIC_EVENTS)
