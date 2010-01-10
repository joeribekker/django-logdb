import datetime

from django.http import HttpResponseBadRequest, HttpResponse
from django.utils import simplejson

from djangologdb.utils import get_datetime
from djangologdb.models import LogEntry

def datasets(request):
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
