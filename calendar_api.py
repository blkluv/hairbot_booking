"""Google Calendar API integration for booking and availability management."""
from __future__ import annotations

# pylint: disable=no-member

from datetime import datetime, timedelta, time as dtime

from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = 'credentials_calendar.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = 'hi@atl5d.com'

SLOTS = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]

# authenticate using the service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# build the calendar service client
service = build('calendar', 'v3', credentials=credentials)


def list_events(date: str):
    """
    Returns a list of events on a specific date.
    Date should be in YYYY-MM-DD format.
    """
    start_dt = datetime.fromisoformat(date)
    end_dt = start_dt + timedelta(days=1)

    start = start_dt.isoformat() + "Z"  # or add timezone-aware datetime
    end = end_dt.isoformat() + "Z"

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start,
        timeMax=end,
        singleEvents=True,
    ).execute()

    return events_result.get('items', [])


def get_free_slots(date: str) -> list:
    """
    Returns a list of available time slots for a given date.
    Respects all-day events like 'holiday' and busy slots.
    """
    events = list_events(date)

    # check a holiday
    if any(
            e.get("summary") == "holiday"
            and e.get("start", {}).get("date") == date
            for e in events
    ):
        return []

    # Get occupied times from events (only if they block time)
    taken_times = []
    for event in events:
        if "dateTime" in event["start"]:
            start_time = event["start"]["dateTime"]
            hour = start_time[11:16]  # extract HH:MM
            taken_times.append(hour)

    return [slot for slot in SLOTS if slot not in taken_times]


def book_slot(date: str, time: str, name: str, service_name: str, username: str = "", phone: str = "") -> bool:
    """
    Books a calendar slot (30 minutes) if it's available.
    Returns True if successful, False if the slot is taken or it's a holiday.
    """
    # Check if it's a holiday or the slot is already taken
    if time not in get_free_slots(date):
        print(f"Cannot book {date} {time}: Slot not available")
        return False

    # Convert date and time into RFC3339 datetime
    start_dt = datetime.fromisoformat(f"{date}T{time}")
    end_dt = start_dt + timedelta(minutes=60)

    description_lines = []

    if username:
        description_lines.append(f"Telegram: https://t.me/{username}")
    if phone:
        description_lines.append(f"Телефон: {phone}")

    description = "\n".join(description_lines) if description_lines else None

    event = {
        "summary": f"{name} — {service_name}",
        "description": description,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "Europe/Lisbon"  # change to your time zone if needed
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "Europe/Lisbon"
        },
        "transparency": "opaque",  # marks time as busy
    }

    service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    print(f"Booked {date} {time} for {name}")
    return True


def set_holiday(date: str) -> bool:
    """
    Creates an all-day 'holiday' event in the calendar for the given date.
    Returns True if created, False if already exists.
    """
    events = list_events(date)

    # check if holiday already exists
    if any(
            e.get("summary") == "holiday" and e.get("start", {}).get("date") == date
            for e in events
    ):
        print(f"Holiday already set for {date}")
        return False

    event = {
        "summary": "holiday",
        "start": {"date": date},
        'end': {'date': (datetime.fromisoformat(date) + timedelta(days=1)).date().isoformat()},
        "transparency": "transparent",  # does not block user's time
        "colorId": "8",
    }

    service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    print(f"Holiday set for {date}")
    return True


def unset_holiday(date: str) -> bool:
    """
    Deletes the 'holiday' event on the given date if it exists.
    """
    events = list_events(date)

    for event in events:
        start_date = event.get("start", {}).get("date")
        summary = event.get("summary", "")

        if summary == "holiday" and start_date == date:
            event_id = event["id"]
            service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
            print(f"Holiday removed for {date}")
            return True
    print(f"No holiday found on {date}")
    return False


from datetime import datetime, timedelta

def find_nearest_slots(days_ahead=30, min_hours_ahead=1.5, max_results=5):
    """
    Returns up to `max_results` available slots starting from now + `min_hours_ahead`,
    searching up to `days_ahead` into the future.
    """
    now = datetime.now() + timedelta(hours=min_hours_ahead)
    results = []

    for i in range(days_ahead):
        date = (now + timedelta(days=i)).date().isoformat()
        free_slots = get_free_slots(date)
        for slot in free_slots:
            slot_dt = datetime.fromisoformat(f"{date}T{slot}")
            if slot_dt > now:
                results.append((date, slot))
                if len(results) >= max_results:
                    return results

    return results

