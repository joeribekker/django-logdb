import logging

from django.http import Http404
from django.utils.encoding import smart_unicode

from djangologdb import settings as djangologdb_settings

logger = logging.getLogger(__name__)

__all__ = ('LoggingMiddleware',)

class LoggingMiddleware(object):
    def process_exception(self, request, exception):
        if not isinstance(exception, Http404):
            logger.info(smart_unicode(exception))
