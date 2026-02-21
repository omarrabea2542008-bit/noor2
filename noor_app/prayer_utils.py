import requests
from datetime import datetime

from database import get_setting, update_settings


def set_location(lat: float, lon: float):
    """Save user location in settings."""
    update_settings('latitude', str(lat))
    update_settings('longitude', str(lon))


def get_location():
    lat = get_setting('latitude', None)
    lon = get_setting('longitude', None)
    if lat is None or lon is None:
        return None, None
    try:
        return float(lat), float(lon)
    except ValueError:
        return None, None


def fetch_prayer_times(lat, lon, date=None):
    """Fetch prayer times for a given date from Aladhan API.
    Returns dict keys: fajr, dhuhr, asr, maghrib, isha, sunrise, sunset etc.
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    url = f'https://api.aladhan.com/v1/timings/{date}?latitude={lat}&longitude={lon}&method=2'
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        times = data.get('data', {}).get('timings', {})
        return {k.lower(): v for k, v in times.items()}
    except Exception as e:
        print('failed to fetch prayer times', e)
        return {}


def get_today_prayer_times():
    """Return prayer times for today, using stored location if available.
    Falls back to default PRAYER_TIMES from islamic_data.
    """
    from islamic_data import PRAYER_TIMES
    lat, lon = get_location()
    if lat is not None and lon is not None:
        times = fetch_prayer_times(lat, lon)
        if times:
            return times
    return PRAYER_TIMES.copy()


def refresh_prayer_times():
    """Utility to update cached times in islamic_data (in-memory)."""
    from islamic_data import PRAYER_TIMES
    times = get_today_prayer_times()
    PRAYER_TIMES.clear()
    PRAYER_TIMES.update(times)
    return PRAYER_TIMES
