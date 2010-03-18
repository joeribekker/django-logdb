# -*- coding: utf-8 -*-
import logging
import datetime
import copy

from django.test import TestCase
from django.core.management import call_command

from djangologdb.models import LogEntry, LogAggregate
from djangologdb.handlers import DjangoDatabaseHandler, add_handler

logger = logging.getLogger()

class LogTest(TestCase):

    def setUp(self):
        # Store logger settings.
        self.old_logger_level = logger.level
        self.old_logger_handlers = copy.copy(logger.handlers)

        # Set up the root logger.
        logger.setLevel(logging.NOTSET)

        # Remove default handlers. Use the copy to prevent early iteration
        # termination.
        for h in self.old_logger_handlers:
            logger.removeHandler(h)

        # Add our handler to the root logger.
        add_handler(logger, DjangoDatabaseHandler())

    def tearDown(self):
        # Remove our own handler.
        for h in logger.handlers:
            logger.removeHandler(h)

        # Restore old logger settings.
        logger.setLevel(self.old_logger_level)

        for h in self.old_logger_handlers:
            logger.addHandler(h)

    def test_handler(self):
        # If the DjangoDatabaseHandler is added to the logging.handlers 
        # namespace, it can be used in file based configurations.
        try:
            from logging.handlers import DjangoDatabaseHandler
        except ImportError:
            self.assert_('The DjangoDatabaseHandler is not present in the logging.handlers namespace after importing it.')

        # Check if our handler was added.
        is_present = False
        for h in logger.handlers:
            if isinstance(h, DjangoDatabaseHandler):
                is_present = True
                break

        self.assertTrue(is_present, 'The DjangoDatabaseHandler was not added to the root logger.')

        # Adding it again should not work.
        add_handler(logger, DjangoDatabaseHandler())

        count = 0
        for h in logger.handlers:
            if isinstance(h, DjangoDatabaseHandler):
                count += 1

        self.assertEqual(count, 1, 'The DjangoDatabaseHandler was added more then once.')

    def test_logging(self):
        msg = '%s is great!'
        args = 'Django'
        extra = {'why': 'Just because!'}

        self.assertEqual(LogEntry.objects.count(), 0)
        logger.log(logging.INFO, msg, args, extra=extra)
        self.assertEqual(LogEntry.objects.count(), 1)

        log_entry = LogEntry.objects.get()

        # Check if the log entry matches.
        self.assertEqual(log_entry.get_message(), msg % args)
        self.assertEqual(log_entry.extra, extra)
        self.assertEqual(log_entry.level, logging.INFO)

        # This time without arguments.
        log_entry.delete()
        logger.log(logging.INFO, msg, extra=extra)
        log_entry = LogEntry.objects.get()

        # Check if the log entry matches.
        self.assertEqual(log_entry.get_message(), msg)
        self.assertEqual(log_entry.extra, extra)
        self.assertEqual(log_entry.level, logging.INFO)

    def test_unicode(self):
        class A:
            def __unicode__(self):
                return u'¿Por qué?'

        class B(object):
            def __unicode__(self):
                return u'No sé.'

        msg = u'¿Qué pasa? %s %s %s %s'
        args = (u'Se me rompió el corazón!', A(), B(), chr(195))
        extra = {'language': u'Español'}

        self.assertEqual(LogEntry.objects.count(), 0)
        # In Python 2.6, you can use:
        # logger.log(logging.INFO, msg, *args, extra=extra)
        logger.log(logging.INFO, msg, args[0], args[1], args[2], args[3], extra=extra)
        self.assertEqual(LogEntry.objects.count(), 1)

        log_entry = LogEntry.objects.get()

        # Check if the log entry matches.
        # Last log entry goes wrong, due to unicode error.
        self.assertEqual(log_entry.get_message(), msg % (args[0:3] + (u'\ufffd',)))
        self.assertEqual(log_entry.level, logging.INFO)
        self.assertEqual(log_entry.extra, extra)

    def test_logging_with_objects(self):
        class A:
            def __repr__(self):
                return 'An instance'

        class B(object):
            def __repr__(self):
                return 'An object'

        msg = '%s, %s, %s, %s and %s are all stringified!'
        args = (A(), B(), ['a', 'list'], A, B)

        self.assertEqual(LogEntry.objects.count(), 0)
        logger.log(logging.INFO, msg, *args)
        self.assertEqual(LogEntry.objects.count(), 1)

        log_entry = LogEntry.objects.get()

        # Check if the log entry matches.
        self.assertEqual(log_entry.get_message(), msg % args)

        # Test if the message itself can also be any of that.
        log_entry.delete()
        for msg in args:
            logger.log(logging.INFO, msg)

            log_entry = LogEntry.objects.get()
            self.assertEqual(log_entry.get_message(), unicode(msg))
            log_entry.delete()

    def _foo(self, level, name):
        """
        A helper function that logs something.
        
        The message arguments (the `name` parameter) should not matter for 
        aggregation. Similar log entries with different `level`s however, should
        not be aggregated.
        """
        logger.log(level, '%s is great', name)

    def test_aggregation(self):
        self._foo(logging.WARNING, 'Django')

        self.assertEqual(LogAggregate.objects.count(), 0)
        call_command('aggregate_logs')
        self.assertEqual(LogAggregate.objects.count(), 1)

        log_aggregate = LogAggregate.objects.get()

        # Check if the log aggregate matches.
        self.assertEqual(log_aggregate.level, logging.WARNING)
        self.assertEqual(log_aggregate.msg, u'%s is great')
        self.assertEqual(log_aggregate.times_seen, 1)

        # Different level, results in a new log aggregate.
        self._foo(logging.CRITICAL, 'Django')

        call_command('aggregate_logs')
        self.assertEqual(LogAggregate.objects.count(), 2)

        # Update and check the first log_aggregate.
        log_aggregate = LogAggregate.objects.get(pk=log_aggregate.pk)
        self.assertEqual(log_aggregate.times_seen, 1)

        # Same level as the first, but different message arguments.
        self._foo(logging.WARNING, 'This')

        call_command('aggregate_logs')
        self.assertEqual(LogAggregate.objects.count(), 2)

        # Update and check the first log_aggregate.
        log_aggregate = LogAggregate.objects.get(pk=log_aggregate.pk)
        self.assertEqual(log_aggregate.times_seen, 2)

    def test_rules(self):
        from djangologdb import settings

        # It is assumed that this test can execute within 1 day ;-) This also
        # overrides any rules set in Django's settings file.
        settings.RULES = [{
            'conditions': {
                'min_level': logging.WARNING,
                'qualname': '',
                'min_times_seen': 3,
                'within_time': datetime.timedelta(1),
            },
            'actions': {
                'level': logging.CRITICAL,
            }
        }]

        self._foo(logging.WARNING, 'This')
        normal_log_entry = LogEntry.objects.get()

        self._foo(logging.WARNING, 'That')
        self._foo(logging.WARNING, 'It')
        self.assertEqual(LogEntry.objects.count(), 3)

        call_command('aggregate_logs')
        self.assertEqual(LogAggregate.objects.count(), 1)
        self.assertEqual(LogEntry.objects.count(), 4)

        rule_log_entry = LogEntry.objects.get(level=logging.CRITICAL)

        # Check if the the rule created log entry is the same as the normal log
        # entry.
        # Note: created, path and name are different.
        self.assertEqual(normal_log_entry.msg, rule_log_entry.msg)
        self.assertEqual(normal_log_entry.extra, rule_log_entry.extra)
        self.assertEqual(normal_log_entry.line_number, rule_log_entry.line_number)
        self.assertEqual(normal_log_entry.thread, rule_log_entry.thread)
        self.assertEqual(normal_log_entry.process, rule_log_entry.process)
