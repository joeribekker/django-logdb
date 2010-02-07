import datetime
import time

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json

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


class JSONField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, basestring) and value:
            try:
                value = json.loads(value)
            except ValueError:
                return None

        return value

    def get_db_prep_save(self, value):
        if value is None:
            return None

        value = json.dumps(value, cls=DjangoJSONEncoder)
        return super(JSONField, self).get_db_prep_save(value)


class TupleField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value is None:
            return None

        if isinstance(value, basestring):
            try:
                value = tuple(json.loads(value))
            except ValueError:
                return None

        return value

    def get_db_prep_save(self, value):
        if value is None:
            return None

        value = json.dumps(value, cls=DjangoJSONEncoder)
        return super(TupleField, self).get_db_prep_save(value)
