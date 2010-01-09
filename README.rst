============
django-logdb
============

Django-logdb enables you to log entries to a database, aggregate and act on 
them with certain rules, and gives you more insight in what's going on.

-----------
Description
-----------

Django-logdb has a custom logging handler that writes log entries to the
database. It therefore integrates nicely with your existing logging 
configuration and you can decide what log entries are written to the database.

The Django admin site is extended with a graphical view of recent log entries
to provide more insight in what is going on. The log messages are grouped by
log level or "type of log entry".

To minimize database access, aggregation is done via a Django command that you
can call periodically or add as cronjob.

-------
Install
-------

The easiest way to install the package is via setuptools::

	easy_install django-logdb

Once installed, update your Django settings.py and add `djangologdb` to your 
INSTALLED_APPS::

	INSTALLED_APPS = (
	    'django.contrib.admin',
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    ...
	    'djangologdb',
	)

Optionally, if you want to log exceptions, add the middleware::

	MIDDLEWARE_CLASSES = (
	    'django.middleware.common.CommonMiddleware',
	    'django.contrib.sessions.middleware.SessionMiddleware',
	    'django.contrib.auth.middleware.AuthenticationMiddleware',
	    ...
	    'djangologdb.middleware.LoggingMiddleware',
	)

To add this handler via Python to, for example, your root logger, you can add
the following to your Django settings.py::

	    import logging
	    from djangologdb.handler import DjangoDatabaseHandler, add_handler
	    
	    logging.basicConfig(level=logging.DEBUG)
	    logger = logging.getLogger()
	    
	    # A bug in Django causes the settings to load twice. Using 
	    # this handler instead of logging.addHandler works around that.
	    add_handler(logger, DjangoDatabaseHandler())
		
To use this handler via a logging configuration file, simply import this module
in your Django settings.py before loading the configuration from a file::

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

TODO: In your Django urls.py (or use Apache's Alias directive)::

	    (r'^media/djangologdb/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '...'}),


Finally, run ``python manage.py syncdb`` to create the database tables.

-------------
Configuration
-------------

TODO

------
Thanks
------

Thanks to David Cramer for his work on django-db-log (http://github.com/dcramer/django-db-log/) on which this package was based.