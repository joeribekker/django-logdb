import datetime
import time

def get_timestamp(date_time):
    """
    Create a `timestamp` from a `datetime` object. A `timestamp` is defined
    as the number of milliseconds since January 1, 1970 00:00. This is like
    Javascript or the Unix timestamp times 1000.
    """
    return time.mktime(date_time.timetuple()) * 1000

def get_datetime(timestamp):
    """
    Takes a `timestamp` and returns a `datetime` object.
    """
    return datetime.datetime.fromtimestamp(int(timestamp / 1000))
