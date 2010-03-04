import logging
import datetime

from django.db import models
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from django.db.models.query import QuerySet

from djangologdb import settings as djangologdb_settings
from djangologdb.utils import get_timestamp, JSONField, TupleField

LOG_LEVELS = (
    (logging.INFO, 'Info'),
    (logging.WARNING, 'Warning'),
    (logging.DEBUG, 'Debug',),
    (logging.ERROR, 'Error'),
    (logging.CRITICAL, 'Critical'),
)

LOG_RECORD_RESERVED_ATTRS = (
    'args', # Always a tuple.
    'created',
    'exc_info', # "Something" that evaluates to True or False.
    'exc_text',
    'filename',
    'funcName',
    'levelname',
    'levelno',
    'lineno',
    'module',
    'msecs',
    'msg',
    'name',
    'pathname',
    'process',
    'processName',
    'relativeCreated',
    'thread',
    'threadName',
    # Additional:
    'message',
    'asctime',
)

class LogQuerySet(QuerySet):

    def get_datasets(self, interval=None, aggregate=None, start_date=None, end_date=None):
        """
        Returns the (graph) datasets, grouped by level or checksum.
        
        The data will be limited to the period from `start_date` to `end_date` 
        with data points per `interval`. Be careful not to generate too many 
        data points (ie. large date range with a small interval).
        
        Note that using a filter on the queryset with the `created` field in 
        combination with the `start_date` or `end_date` arguments can lead to 
        unexpected results. These arguments are added for convenience.
        
        **Arguments**
        
        ``interval``
            Aggregate the number of logs over this `datetime.timedelta`
            interval. The default is 1 day.
            
        ``aggregate``
            Indicates what to group the logs by. This can be either the string
            'checksum' or 'level'. The default is 'level'.
        
        ``start_date``
            Begin the datasets from this `datetime.datetime`. The default is the
            first `LogEntry` object in the queryset.
        
        ``end_date``
            A `datetime.datetime` to end the period for the datasets. The
            default is the last `LogEntry` in the queryset.
        
        """
        datasets = {}

        # Note that calls to self return new querysets.
        if start_date is None:
            oldest = self.order_by('created')[:1]
            if len(oldest) == 0:
                return datasets
            start_date = oldest[0].created
        if end_date is None:
            latest = self.order_by('-created')[:1]
            if len(latest) == 0:
                return datasets
            end_date = latest[0].created
        if start_date > end_date:
            raise ValueError('The end_date needs to be higher than the start_date.')
        if interval is None:
            interval = datetime.timedelta(1)
        if aggregate is None:
            aggregate = 'level'
        elif aggregate not in ['level', 'checksum']:
            raise ValueError('The aggregate needs to be either \'checksum\' or \'level\'.')

        # Get all the levels used in the specified date range and prepare the
        # datasets.
        if aggregate == 'checksum':
            for entry in self.filter(created__range=(start_date, end_date)).exclude(log_aggregate__checksum=None).values('log_aggregate__name', 'log_aggregate__checksum').distinct():
                datasets[entry['log_aggregate__checksum']] = {
                    'label': entry['log_aggregate__name'],
                    'data': [],
                }
        else:
            for level in self.filter(created__range=(start_date, end_date)).values_list('level', flat=True).distinct():
                datasets[level] = {
                    'label': logging.getLevelName(level),
                    'data': [],
                }
                if level in djangologdb_settings.LEVEL_COLORS:
                    datasets[level]['color'] = djangologdb_settings.LEVEL_COLORS[level]

        current_date = start_date
        # FIXME: It is not possible to group by a certain interval (for example:
        # by month, by hour) via the Django ORM, hence we execute 1 query per 
        # interval.
        while(current_date < end_date):
            # Get the number of log entries per level or checksum.
            if aggregate == 'checksum':
                stats = self.filter(created__range=(current_date, current_date + interval)).values('log_aggregate__checksum').annotate(log_count=Count('level')).values_list('log_aggregate__checksum', 'log_count')
            else:
                stats = self.filter(created__range=(current_date, current_date + interval)).values('level').annotate(log_count=Count('level')).values_list('level', 'log_count')
            aggregated_logs = dict(stats)
            timestamp = get_timestamp(current_date)

            for aggr, dataset in datasets.items():
                dataset['data'].append([timestamp, aggregated_logs[aggr] if aggregated_logs.has_key(aggr) else 0])

            current_date += interval

        return datasets

class LogManager(models.Manager):

    def get_query_set(self):
        return LogQuerySet(self.model)

    def get_datasets(self, *args, **kwargs):
        return self.get_query_set().get_datasets(*args, **kwargs)

    def _get_extra(self, record):
        """
        Get the extra fields by filtering out the known reserved fields.
        
        Note: Values are stringified to prevent deep pickling.
        """
        extra = {}
        for k, v in record.__dict__.items():
            if k not in LOG_RECORD_RESERVED_ATTRS:
                extra[k] = unicode(v) # Stringify
        return extra

    def create_from_record(self, record):
        """
        Creates an error log for a `logging` module `record` instance. This is
        done with as little overhead as possible.

        NOTE: The message and message arguments are stringified in case odd 
        objects are passed, even though this should be up to the user.
        """
        # Try to convert all arguments to unicode.
        try:
            args = map(unicode, record.args)
        except UnicodeDecodeError:
            args = []
            for arg in record.args:
                try:
                    args.append(unicode(arg))
                except UnicodeDecodeError:
                    # If a specific argument goes wrong, try to replace the
                    # invalid characters.
                    try:
                        args.append(unicode(arg, errors='replace'))
                    except:
                        args.append(u'(django-logdb: Argument encoding error)')
                except:
                    args.append(u'(django-logdb: Incorrect argument)')

        # Try to convert the message to unicode.
        try:
            msg = unicode(record.msg)
        except UnicodeDecodeError:
            try:
                msg = unicode(record.msg, errors='replace')
            except:
                msg = u'(django-logdb: Message encoding error)'

        log_entry = LogEntry.objects.create(
            args=tuple(args),
            exc_text=record.exc_text,
            filename=record.filename,
            function_name=record.funcName,
            level=record.levelno,
            line_number=record.lineno,
            module=record.module,
            msg=msg,
            name=record.name,
            path=record.pathname,
            process=record.process,
            process_name=record.processName if hasattr(record, 'processName') else None,
            thread=record.thread,
            thread_name=record.threadName,
            extra=self._get_extra(record),
        )
        return log_entry

class BaseLogEntry(models.Model):
    """
    Basic log entry fields.
    """
    filename = models.CharField(max_length=50, blank=True, null=True)
    function_name = models.CharField(max_length=50, blank=True, null=True)
    level = models.PositiveIntegerField(choices=LOG_LEVELS, default=logging.CRITICAL, db_index=True)
    line_number = models.PositiveIntegerField(default=0)
    module = models.CharField(max_length=50, blank=True, null=True)
    msg = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=200, default='root', db_index=True)
    path = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        abstract = True

class LogAggregate(BaseLogEntry):
    """
    An aggregation of various similar log entries.
    """
    times_seen = models.PositiveIntegerField(default=1)
    last_seen = models.DateTimeField(auto_now=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    checksum = models.CharField(max_length=32, unique=True)

    def __unicode__(self):
        return u'%s, %d' % (self.filename, self.line_number)

class LogEntry(BaseLogEntry):
    """
    Represents a single log entry from the `logger` module. Most of the `logger`
    fields are represented in this model, except for some time related fields.
    """
    args = TupleField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    exc_text = models.TextField(blank=True, null=True)
    process = models.PositiveIntegerField(default=0)
    process_name = models.CharField(max_length=200, blank=True, null=True)
    thread = models.DecimalField(max_digits=21, decimal_places=0)
    thread_name = models.CharField(max_length=200, blank=True, null=True)
    extra = JSONField(blank=True)

    log_aggregate = models.ForeignKey(LogAggregate, blank=True, null=True)

    objects = LogManager()

    class Meta:
        verbose_name_plural = _('Log entries')

    def get_message(self):
        if not self.args:
            return self.msg

        try:
            return self.msg % self.args
        except TypeError, e:
            return u'Failed to render message: %s' % e

    def get_message_display(self):
        msg = self.get_message()
        if len(msg) > 40:
            return u'%s [...]' % msg[:35]
        else:
            return u'%s' % msg
    get_message_display.short_description = _('message')

    def __unicode__(self):
        return self.get_message_display()
