import logging

from django.http import Http404
from django.utils.encoding import smart_unicode

logger = logging.getLogger(__name__)

__all__ = ('LoggingMiddleware',)

class LoggingMiddleware(object):
    def process_exception(self, request, exception):
        if not isinstance(exception, Http404):
            logger.error(smart_unicode(exception), exc_info=True)
