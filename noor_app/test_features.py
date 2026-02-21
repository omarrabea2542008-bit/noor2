import os
import sqlite3
from datetime import datetime, timedelta

from hijri_utils import gregorian_to_hijri, get_hijri_date
from database import (
    set_ramadan_plan, get_ramadan_plan, add_ramadan_pages, get_ramadan_daily_target,
    get_statistics, update_settings, get_setting
)


def test_hijri_conversion():
    # check that known date 2021-04-13 -> 1442-09-01 (start of Ramadan 1442)
    d = datetime(2021,4,13)
    y,m,day = gregorian_to_hijri(d)
    assert (y,m,day) == (1442,9,1)
    formatted = get_hijri_date()
    assert len(formatted.split('/')) == 3


def test_prayer_utils():
    from prayer_utils import fetch_prayer_times, set_location, get_location, get_today_prayer_times
    lat, lon = get_location()
    # set a dummy location
    set_location(21.3891, 39.8579)  # makkah
    lat2, lon2 = get_location()
    assert abs(lat2 - 21.3891) < 0.001
    assert abs(lon2 - 39.8579) < 0.001
    times = fetch_prayer_times(lat2, lon2)
    assert 'fajr' in times
    todays = get_today_prayer_times()
    assert isinstance(todays, dict)


def test_reading_log():
    from database import log_reading, get_reading_pages, get_average_reading
    # purge existing for today
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect('noor.db')
    c = conn.cursor()
    c.execute('DELETE FROM reading_log WHERE date = ?', (today,))
    conn.commit()
    log_reading(5)
    assert get_reading_pages(today) >= 5
    avg = get_average_reading(1)
    assert avg >= 5

    # also ensure QuranScreen increments log when navigating
    from screens import QuranScreen
    qs = QuranScreen()
    # clear again
    c.execute('DELETE FROM reading_log WHERE date = ?', (today,))
    conn.commit()
    qs.next_ayah(None)
    assert get_reading_pages(today) >= 1


def test_events():
    from islamic_data import ISLAMIC_EVENTS
    assert (9,1) in ISLAMIC_EVENTS


def test_ramadan_calendar():
    from screens import RamadanPlanScreen
    r = RamadanPlanScreen()
    # ensure no plan returns empty
    assert r.get_ramadan_calendar() == []
    # set a plan and check length
    from database import set_ramadan_plan
    set_ramadan_plan(3)
    cal = r.get_ramadan_calendar()
    assert len(cal) == 3


def test_ramadan_plan_stats():
    from statistics import get_ramadan_plan_stats
    from database import set_ramadan_plan
    set_ramadan_plan(5)
    stats = get_ramadan_plan_stats()
    assert stats['plan_days'] == 5
    assert 'avg_per_day' in stats


def test_ramadan_plan_flow():
    # clear existing plan
    conn = sqlite3.connect('noor.db')
    c = conn.cursor()
    c.execute('DELETE FROM ramadan_plan')
    conn.commit()

    assert get_ramadan_plan() is None
    set_ramadan_plan(10)
    plan = get_ramadan_plan()
    assert plan['plan_days'] == 10
    assert plan['pages_read'] == 0
    target = get_ramadan_daily_target()
    assert target == (604 + 9)//10
    new = add_ramadan_pages(20)
    assert new == 20
    # complete
    add_ramadan_pages(584)
    assert add_ramadan_pages(0) >= 604


if __name__ == '__main__':
    test_hijri_conversion()
    test_prayer_utils()
    test_reading_log()
    test_events()
    test_ramadan_calendar()
    test_ramadan_plan_flow()
    print("all tests passed")
