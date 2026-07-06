from datetime import datetime, timedelta
from typing import Any

def get_current_date_info() -> dict[str, Any]:
    """Get the relative calendar dates for today, tomorrow, and yesterday.

    Use this tool IMMEDIATELY whenever the user uses relative time terms like
    'hari ini' (today), 'besok' (tomorrow), 'kemarin' (yesterday),
    'lusa' (day after tomorrow), or asks for the current date/day.

    Returns:
        A dictionary containing dates in 'YYYY-MM-DD' format and the day names.
    """

    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)

    days_id = {
        "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
        "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
    }

    return {
        "today": {
            "date": today.strftime("%Y-%m-%d"),
            "day_name": days_id.get(today.strftime("%A"), today.strftime("%A"))
        },
        "tomorrow": {
            "date": tomorrow.strftime("%Y-%m-%d"),
            "day_name": days_id.get(tomorrow.strftime("%A"), tomorrow.strftime("%A"))
        },
        "yesterday": {
            "date": yesterday.strftime("%Y-%m-%d"),
            "day_name": days_id.get(yesterday.strftime("%A"), yesterday.strftime("%A"))
        },
        "day_after_tomorrow": {
            "date": day_after_tomorrow.strftime("%Y-%m-%d"),
            "day_name": days_id.get(day_after_tomorrow.strftime("%A"), day_after_tomorrow.strftime("%A"))
        }
    }