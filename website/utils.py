from datetime import datetime, timezone, timedelta

# Define UTC+8 timezone offset
utc_plus_8 = timezone(timedelta(hours=8))

def get_local_time():
    """Returns the current date and time in UTC+8."""
    return datetime.now(timezone.utc).astimezone(utc_plus_8)

def get_current_time():
    """Returns the current date and time in UTC+8."""
    return datetime.now(timezone.utc).astimezone(utc_plus_8)

def get_current_year():
    """Returns the current year in UTC+8."""
    return get_current_time().year

def time_since(dt):
    """Returns a string representing how long ago a date was, using UTC+8 timezone."""
    now = get_current_time()
    diff = now - dt

    seconds = diff.total_seconds()
    if seconds < 60:
        return f"{int(seconds)} second{'s' if seconds != 1 else ''} ago"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{int(minutes)} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{int(hours)} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 2592000:
        days = seconds // 86400
        return f"{int(days)} day{'s' if days != 1 else ''} ago"
    elif seconds < 31536000:
        months = seconds // 2592000
        return f"{int(months)} month{'s' if months != 1 else ''} ago"
    else:
        years = seconds // 31536000
        return f"{int(years)} year{'s' if years != 1 else ''} ago"


