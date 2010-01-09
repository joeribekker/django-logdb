import datetime

from django.conf.urls.defaults import patterns
from django.contrib import admin
from django.utils.translation import ugettext
from django.utils.encoding import force_unicode
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson

from models import LogEntry, LogAggregate
from djangologdb.utils import get_datetime

class LogEntryInline(admin.TabularInline):
    model = LogEntry

class LogAggregateOptions(admin.ModelAdmin):
    list_display = ('name', 'module', 'function_name', 'line_number', 'level', 'last_seen', 'times_seen',)
    list_filter = ('name', 'level',)
    date_hierarchy = 'last_seen'
    ordering = ('-last_seen',)
    inlines = (LogEntryInline,)

    def change_view(self, request, object_id, extra_context=None):
        djangologdb_context = {
            'aggregate': 'checksum',
            'title': ugettext('View %s') % force_unicode(self.opts.verbose_name)
        }
        return super(LogAggregateOptions, self).change_view(request,
            object_id, extra_context=djangologdb_context)

    def changelist_view(self, request, extra_context=None):
        djangologdb_context = {
            'aggregate': 'checksum',
            'title': ugettext('Select %s to view') % force_unicode(self.opts.verbose_name)
        }
        return super(LogAggregateOptions, self).changelist_view(request,
            extra_context=djangologdb_context)

class LogEntryOptions(admin.ModelAdmin):
    list_display = ('created', 'level', 'name', 'module', 'function_name', 'line_number', 'process', 'thread', 'get_message_display', 'extra')
    list_filter = ('name', 'level',)
    date_hierarchy = 'created'
    ordering = ('-created',)

    def changelist_view(self, request, extra_context=None):
        djangologdb_context = {
            'aggregate': 'level',
            'title': ugettext('Select %s to view') % force_unicode(self.opts.verbose_name)
        }
        return super(LogEntryOptions, self).changelist_view(request,
            extra_context=djangologdb_context)

    def get_urls(self):
        urls = super(LogEntryOptions, self).get_urls()
        djangologdb_urls = patterns('',
            (r'^datasets/$', self.datasets_view)
        )
        return djangologdb_urls + urls

    def datasets_view(self, request):
        """
        Returns a JSON encoded string containing the datasets. This view takes 
        similar arguments as the regular `get_datasets` function, but as 
        GET-parameters.
        
        This allows you to do cool stuff on the admin site.
        
        ``id``
            The ``LogEntry`` object ID to filter on.
        
        ``start_date``
            A Javascript timestamp indicating the start date for the datasets.

        ``end_date``
            A Javascript timestamp indicating the end date of the datasets.
            
        ``aggregate``
            String that can either be 'level' or 'checksum'.
            
        ``interval_days`` and ``interval_seconds``
            Integers that create a `datetime.timedelta` object.
        """
        id = request.GET.get('id', None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        aggregate = request.GET.get('aggregate', None)
        interval_days = request.GET.get('interval_days', 0)
        interval_seconds = request.GET.get('interval_seconds', 0)

        if interval_days == 0 and interval_seconds == 0:
            interval = None
        else:
            interval = datetime.timedelta(int(interval_days), int(interval_seconds))

        try:
            if start_date is not None:
                start_date = get_datetime(int(start_date))
            if end_date is not None:
                end_date = get_datetime(int(end_date))

            if id is None:
                queryset = LogEntry.objects.all()
            else:
                queryset = LogEntry.objects.filter(pk=int(id))

            result = queryset.get_datasets(start_date=start_date, end_date=end_date, aggregate=aggregate, interval=interval)
        except:
            return HttpResponseBadRequest()

        return HttpResponse(simplejson.dumps(result), mimetype='text/json')

admin.site.register(LogAggregate, LogAggregateOptions)
admin.site.register(LogEntry, LogEntryOptions)
