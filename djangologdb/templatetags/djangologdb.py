import logging

from django.template import Library
from django.db.models import Count

register = Library()

def djangologdb_media_prefix():
    """
    Returns the string contained in the setting ADMIN_MEDIA_PREFIX.
    """
    try:
        from django.conf import settings
    except ImportError:
        return ''
    return settings.ADMIN_MEDIA_PREFIX
djangologdb_media_prefix = register.simple_tag(djangologdb_media_prefix)

def djangologdb_datasets(change_list):
    # from djangologdb.models import LogEntry, LogAggregate
    #print change_list.get_query_set()._as_sql()
    data = change_list.query_set.values('level').annotate(log_count=Count('level')).values_list('level', 'log_count')
    level_data = dict(data)

    datasets = {}
    for level in level_data.keys():
        level_name = logging.getLevelName(level)
        datasets[level] = {
            'label': level_name,
            'data': [],
        }

    print change_list.query_set.filter(('created__day', 24)).values('level').annotate(log_count=Count('level'))
    print change_list.model.objects.filter(('created__day', 24)).values('level').annotate(log_count=Count('level'))

    for x in range(1, 32):
        # TODO: Optimize this query. There is no generic way to group by a date
        # part, hence we use a filter (which can use a generic way).
        data = change_list.query_set.filter(created__day=x).annotate(Count('level')).values_list('level', 'level__count')
        existing_log_data = dict(data)
        # DJANGO BUG: Try to do _as_sql() on this queryset.

        for level in level_data.keys():
            datasets[level]['data'].append([x, existing_log_data[x] if existing_log_data.has_key(x) else 0])

    return datasets
djangologdb_datasets = register.simple_tag(djangologdb_datasets)
