DJANGO-LOGDB
============

Django-logdb enables you to log entries to a database, aggregate and act on 
them with certain rules, and gives you more insight in what's going on.

Description
-----------

Django-logdb has a custom logging handler that writes log entries to the
database. It therefore integrates nicely with your existing logging 
configuration and you can decide what log entries are written to the database.

The Django admin site is extended with a graphical view of recent log entries
to provide more insight in what is going on. The log messages are grouped by
log level or "type of log entry".

To minimize database access, aggregation is done via a Django command that you
can call periodically (as a cronjob).

Install
-------

The easiest way to install the package is via setuptools::

    easy_install django-logdb

Once installed, update your Django `settings.py` and add ``djangologdb`` to your 
INSTALLED_APPS::

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        ...
        'djangologdb',
    )

In your Django `urls.py`, include the `djangologdb.urls` before the admin::

    urlpatterns = patterns('',
        ...
        (r'^admin/djangologdb/', include('djangologdb.urls')),
        ...
        (r'^admin/', include(admin.site.urls)),
    )

Optionally, if you want to log exceptions, add the middleware::

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        ...
        'djangologdb.middleware.LoggingMiddleware',
    )

Run ``python manage.py syncdb`` to create the database tables.

Setup logging
-------------

Now, for the actual logging part, you should use the database logging handler.
There are two ways to do this: Using only Python code, or, by using a 
configuration file. Both methods are explained below. 

To add this handler via Python to, for example, your root logger, you can add
the following to your Django `settings.py`::

    import logging
    from djangologdb.handler import DjangoDatabaseHandler, add_handler
    
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    
    # A bug in Django causes the settings to load twice. Using 
    # this handler instead of logging.addHandler works around that.
    add_handler(logger, DjangoDatabaseHandler())
        
To use this handler via a logging configuration file, simply import the 
``handlers`` module from ``djangologdb`` in your Django `settings.py` before 
loading the configuration from a file::

    from djangologdb import handlers
    logging.config.fileConfig(...)
    
Then in your logging configuration file, you can add it from the handlers 
namespace and add it to any logger you want::

    [handlers]
    keys=djangologdb
    
    [logger_root]
    level=NOTSET
    handlers=djangologdb
    
    [handler_djangologdb]
    class=handlers.DjangoDatabaseHandler
    args=()

Configuration
-------------

You can set the following settings in your Django `settings.py` file:

LOGDB_HISTORY_DAYS
	The number of days to show in the various graphs.
	
	Default::
	
		LOGDB_HISTORY_DAYS = 30

LOGDB_INTERVAL
	The ``timedelta`` between each datapoint in the various graphs.
	
	Default::

		LOGDB_INTERVAL = datetime.timedelta(1) # 1 day

LOGDB_RULES
    Define rules to create a new log entry when certain conditions are true.
    
    Default::
    
        LOGDB_RULES = 
            [{
                # If 3 logs with level WARNING or higher occur in 5 minutes or
                # less, create a new log with level CRITICAL.
                'conditions': {
                    'min_level': logging.WARNING,
                    'qualname': '',
                    'min_times_seen': 3,
                    'within_time': datetime.timedelta(0, 5 * 60),
                },
                'actions': {
                    'level': logging.CRITICAL,
                }
            }]

LOGDB_LEVEL_COLORS
    Set colors to use in the graph for level based datasets.

    Default::
    
        LOGDB_LEVEL_COLORS =
            {
                logging.DEBUG: '#c2c7d1',
                logging.INFO: '#aad2e9',
                logging.WARNING: '#b9a6d7',
                logging.ERROR: '#deb7c1',
                logging.CRITICAL: '#e9a8ab',
            }

LOGDB_MEDIA_ROOT
    Set the absolute path to the directory of `django-logdb` media.
    
    Default::
        
        LOGDB_MEDIA_ROOT = os.path.join(djangologdb.__path__[0], 'media')
    
LOGDB_MEDIA_URL
    Set the URL that handles the media served from ``LOGDB_MEDIA_ROOT``. Make 
    sure to add a trailing slash at the end. If ``settings.DEBUG=True``, the 
    media will be served by Django.
    
    Default::    
    
        LOGDB_MEDIA_URL = '/admin/djangologdb/media/'

Commands
--------

aggregate_logs
    Aggregates log entries and triggers any action with matching rules. 
    
    *Usage*:
        ``python django-admin.py aggregate_logs``
        
    *Options*:
        -s, --skip-actions    Do not use the rules to create new logs.
        --cleanup=CLEANUP     Specifies the number of days to keep log entries
                              and deletes the rest.

FAQ
---

The graph doesn't show in the Django admin.
    If you don't have ``settings.DEBUG=True``, the media will not be served by 
    Django. You should copy the media directory to your own media directory and
    set LOGDB_MEDIA_ROOT and LOGDB_MEDIA_URL accordingly.
    
    Example::
    	
    	LOGDB_MEDIA_ROOT = '/myproject/media/djanglogdb/'
    	LOGDB_MEDIA_URL = '/media/djanglogdb/'
    
    Instead of copying, you can also use Apache's Alias directive to serve the 
    static files, as you probably also did for Django's own media files. It is
    explained here: http://docs.djangoproject.com/en/dev/howto/deployment/modwsgi/#serving-media-files
    This boils down to adding the following line to your VirtualHost entry::
    
    	Alias <your LOGDB_MEDIA_URL setting> <path to django-logdb media dir>
    
    Example::

		Alias /admin/djangologdb/media/ /myproject/eggs/django_logdb-0.9.5-py2.6.egg/djangologdb/media/

The Django admin pages for django-logdb load very slow.
    If you have a lot of datapoints in the graph, it executes a lot of queries.
    This can take some time. You should decrease the time period or increase the
    interval. By default, the last 30 days with an interval of 1 day is used, 
    resulting in 30 datapoints.
    See the settings ``LOGDB_HISTORY_DAYS`` and ``LOGDB_INTERVAL``.
    
Why is there 1 query executed for each datapoint?
    Django does not (yet) allow to group by certain date information. Even 
    though a timestamp is stored in the database, there is no way to tell the 
    Django ORM to group by day, by hour, etc. The solution I used was to 
    filter/limit the results needed to construct 1 datapoint.

When I run my tests, I see ``ERROR:djangologdb.middleware`` [...]
    When you run, for example, the testproject, the configuration is set so
    that any error is also displayed on ``sys.stderr``. As you you'll see, the
    tests all succeed but the exceptions that are tested are just displayed in
    the console. This is not an error!

    You can disable this behaviour by disabling logging to the console for your
    test configuration (ie. remove the handler).


Thanks
------
To the various people that helped making this project better and better:

- Maciek Szczesniak (vvarp)
- Victor van den Elzen

Thanks to David Cramer for his work on django-db-log 
(http://github.com/dcramer/django-db-log/) on which this package was based.