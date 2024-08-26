import datetime as dt

def get_current_datetime(tz_unit=7):
    return dt.datetime.utcnow() + dt.timedelta(hours=tz_unit)

# Create a function to get today if it is from Monday to Friday, otherwise get the last trading day
def get_recent_trading_day():
    today = get_current_datetime()
    if today.weekday() == 5 or today.hour <= 5:
        return today - dt.timedelta(days=1)
    
    if today.weekday() == 6:
        return today - dt.timedelta(days=2)

    return today