# Global settings for django-logdb.
import logging
import datetime
import os

from django.conf import settings

import djangologdb

INTERVAL = getattr(settings, 'LOGDB_INTERVAL', datetime.timedelta(1))

HISTORY_DAYS = getattr(settings, 'LOGDB_HISTORY_DAYS', 30)

RULES = getattr(settings, 'LOGDB_RULES',
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
LEVEL_COLORS = getattr(settings, 'LOGDB_LEVEL_COLORS',
    {
        logging.DEBUG: '#c2c7d1',
        logging.INFO: '#aad2e9',
        logging.WARNING: '#b9a6d7',
        logging.ERROR: '#deb7c1',
        logging.CRITICAL: '#e9a8ab',
    }
)

MEDIA_ROOT = getattr(settings, 'LOGDB_MEDIA_ROOT', os.path.join(djangologdb.__path__[0], 'media'))
MEDIA_URL = getattr(settings, 'LOGDB_MEDIA_URL', '/admin/djangologdb/media/')
