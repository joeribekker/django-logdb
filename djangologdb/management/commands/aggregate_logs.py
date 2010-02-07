from optparse import make_option
import logging
import datetime

from django.core.management.base import NoArgsCommand
from django.utils.hashcompat import md5_constructor
from django.db.models import F
from django.db import transaction

from djangologdb.models import LogEntry, LogAggregate
from djangologdb import settings as djangologdb_settings

logger = logging.getLogger(__name__)

class Command(NoArgsCommand):
    help = 'Aggregates log entries.'

    requires_model_validation = True
    output_transaction = True
    can_import_settings = True

    option_list = NoArgsCommand.option_list + (
        make_option('-s', '--skip-actions', dest='skip_actions', action='store_true', help='Do not use the rules to create new logs.'),
        make_option('--cleanup', dest='cleanup', default='-1', help='Specifies the number of days to keep log entries and deletes the rest.'),
    )

    @transaction.commit_on_success
    def handle_noargs(self, **options):
        self.verbosity = int(options.get('verbosity', 1))
        self.skip_actions = options.get('skip_actions', False)
        self.cleanup = int(options.get('cleanup', -1))

        recent_log_aggregates = {}

        # Process un-aggregated entries.
        for log_entry in list(LogEntry.objects.filter(log_aggregate=None).order_by('-created')):
            # Create checksum.
            entries = {
                'filename': log_entry.filename,
                'function_name': log_entry.function_name,
                'level': log_entry.level,
                'line_number': log_entry.line_number,
                'module': log_entry.module,
                'msg': log_entry.msg,
                'name': log_entry.name,
                'path': log_entry.path,
            }
            checksum = md5_constructor(str(entries))

            entries.update({
                'first_seen': log_entry.created,
                'last_seen': log_entry.created,
            })

            # Create log aggregate if none exists for this log entry.
            log_aggregate, is_created = LogAggregate.objects.get_or_create(
                checksum=checksum.hexdigest(),
                defaults=entries
            )

            # Update log aggregate if it already existed.
            if not is_created:
                log_aggregate.times_seen = F('times_seen') + 1
                log_aggregate.last_seen = log_entry.created
                log_aggregate.save()

            log_entry.log_aggregate = log_aggregate
            log_entry.save()

            # Use an entry to have all the variables.
            recent_log_aggregates[log_aggregate.id] = log_entry

        # Only process recently created or updated log aggregates.
        if not self.skip_actions:
            for log_entry in recent_log_aggregates.values():
                actions = self._get_matching_rule_actions(log_aggregate)
                if actions is not None:
                    additional_record = logger.makeRecord('django-logdb: %s' % log_entry.name, actions['level'], log_entry.filename, log_entry.line_number, log_entry.msg, log_entry.args, None, log_entry.function_name, extra=log_entry.extra)
                    logger.handle(additional_record)

        # Delete old log entries.
        if self.cleanup >= 0:
            LogEntry.objects.exclude(created__gt=datetime.datetime.now() - datetime.timedelta(self.cleanup)).delete()

    def _get_matching_rule_actions(self, log_aggregate):
        """
        Check if there is a rule that matches the `log_aggregate` and return it.
        
        This is done by settings rather then a database model to prevent 
        additional overhead. The idea is that there are not that many rules, nor
        the desire to manage them often.
        """
        for rule in djangologdb_settings.RULES:

            # TODO: Is that F() method in times_seen conflicting here?

            # Inexpensive condition checks first. If the log has the same level
            # as the (only possible) action would result in, skip it.
            if log_aggregate.level != rule['actions']['level'] and \
                    log_aggregate.level >= rule['conditions']['min_level'] and \
                    log_aggregate.name.startswith(rule['conditions']['qualname']) and \
                    log_aggregate.times_seen >= rule['conditions']['min_times_seen']:

                # Perform condition check which requires a database hit.
                latest_log_entries = log_aggregate.logentry_set.all().order_by('-created')[:rule['conditions']['min_times_seen']]
                times_seen = len(latest_log_entries)
                if times_seen == rule['conditions']['min_times_seen'] and \
                        latest_log_entries[0].created - latest_log_entries[times_seen - 1].created <= rule['conditions']['within_time']:
                    return rule['actions']

        return None
