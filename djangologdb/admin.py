from django.contrib import admin
from django.utils.translation import ugettext
from django.utils.encoding import force_unicode

from models import LogEntry, LogAggregate

class LogEntryInline(admin.TabularInline):
    model = LogEntry

class LogAggregateOptions(admin.ModelAdmin):
    list_display = ('name', 'module', 'function_name', 'line_number', 'level', 'last_seen', 'times_seen',)
    list_filter = ('name', 'level',)
    date_hierarchy = 'last_seen'
    ordering = ('-last_seen',)
    inlines = (LogEntryInline,)

    # Use different names to work with custom Django admin templates.
    change_form_template = 'admin/djangologdb/logaggregate/logdb_change_form.html'
    change_list_template = 'admin/djangologdb/logdb_change_list.html'

    def change_view(self, request, object_id, extra_context=None):
        djangologdb_context = {
            'aggregate': 'checksum',
            'title': ugettext('View %s') % force_unicode(self.opts.verbose_name),
        }
        return super(LogAggregateOptions, self).change_view(request,
            object_id, extra_context=djangologdb_context)

    def changelist_view(self, request, extra_context=None):
        djangologdb_context = {
            'aggregate': 'checksum',
            'title': ugettext('Select %s to view') % force_unicode(self.opts.verbose_name),
        }
        return super(LogAggregateOptions, self).changelist_view(request,
            extra_context=djangologdb_context)

class LogEntryOptions(admin.ModelAdmin):
    list_display = ('created', 'level', 'name', 'module', 'function_name', 'line_number', 'process', 'thread', 'get_message_display', 'extra')
    list_filter = ('name', 'level',)
    date_hierarchy = 'created'
    ordering = ('-created',)

    # Use different names to work with custom Django admin templates.
    change_list_template = 'admin/djangologdb/logdb_change_list.html'

    def changelist_view(self, request, extra_context=None):
        djangologdb_context = {
            'aggregate': 'level',
            'title': ugettext('Select %s to view') % force_unicode(self.opts.verbose_name),
        }
        return super(LogEntryOptions, self).changelist_view(request,
            extra_context=djangologdb_context)

admin.site.register(LogAggregate, LogAggregateOptions)
admin.site.register(LogEntry, LogEntryOptions)
