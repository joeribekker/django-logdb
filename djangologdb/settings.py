# Global settings for django-logdb.

import logging
import datetime

from django.conf import settings

RULES = getattr(settings, 'DJANGO_LOGDB_RULES',
    [{
        # If 3 logs with level WARNING or higher occur in 5 minutes or less, 
        # create a new log with level CRITICAL.
        'conditions': {
            'min_level': logging.WARNING,
            'qualname': '',
            'min_times_seen': 3,
            'within_time': datetime.timedelta(0, 5 * 60),
        },
        'actions': {
            'level': logging.CRITICAL,
        }
    }]
)

# Set colors to use in the graph for level based datasets.
LEVEL_COLORS = getattr(settings, 'DJANGO_LOGDB_LEVEL_COLORS',
    {
        logging.DEBUG: '#c2c7d1',
        logging.INFO: '#aad2e9',
        logging.WARNING: '#b9a6d7',
        logging.ERROR: '#deb7c1',
        logging.CRITICAL: '#e9a8ab',
    }
)

# Indicate what HTTP responses with a certain status to log and with what level. 
HTTP_STATUS_LOGGING = getattr(settings, 'LOGDB_HTTP_STATUS_LOGGING',
    {
        'Http500': logging.ERROR,
    }
)
