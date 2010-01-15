import logging
import datetime

from django import forms
from django.shortcuts import render_to_response

from djangologdb.models import LOG_LEVELS

logger = logging.getLogger()

class LogForm(forms.Form):
    level = forms.ChoiceField(choices=LOG_LEVELS, required=True, initial=logging.INFO)

def index(request):
    if request.method == 'POST':
        form = LogForm(request.POST)
        if form.is_valid():
            logger.log(int(form.cleaned_data['level']), 'Submitted form on %s.', datetime.date.today(), extra={'ip_address': request.META.get('REMOTE_ADDR', '')})
            msg = 'Form submitted.'
    else:
        form = LogForm()
        msg = ''

    return render_to_response('index.html', {
        'form': form,
        'msg': msg,
    })
