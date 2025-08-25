import calendar
from datetime import datetime, timedelta


def get_month_range(month, year):
    # Convert month name to month number
    month_number = datetime.strptime(month, "%B").month
    # Get the first day of the month
    start_date = datetime(year, month_number, 1)
    # Get the last day of the month
    end_date = datetime(year, month_number, calendar.monthrange(year, month_number)[1])
    return start_date.date(), end_date.date()


def get_current_week_range():
    # Get today's date
    today = datetime.today()
    # Get the start of the current week (Monday)
    start_date = today - timedelta(days=today.weekday())
    # Get the end of the current week (Sunday)
    end_date = start_date + timedelta(days=6)
    return start_date.date(), end_date.date()


def get_current_month_range():
    today = datetime.today()
    start_date, end_date = get_month_range(today.month, today.year)
    return start_date, end_date
