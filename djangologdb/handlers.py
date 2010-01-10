import logging
import logging.handlers

class DjangoDatabaseHandler(logging.Handler):
    """
    Handler for logging to the database as configured in Django.
    
    To add this handler via Python to your root logger, you can add the 
    following to your Django settings::
    
        import logging
        from djangologdb.handler import DjangoDatabaseHandler
        
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger()
        
        logger.addHandler(DjangoDatabaseHandler())

        # Note: There is a bug in Django that loads the settings twice, and thus
        # adds this handler twice. You need to take care of that yourself, or
        # use the shortcut helper function instead of `logger.addHandler`:
        # 
        # from djangologdb.handler import add_handler
        # add_handler(logger, DjangoDatabaseHandler())
        
    To use this handler via a config file, simply import this module in your
    Django settings before loading the configuration from a file::
    
        from djangologdb import handlers
        # logging.config.fileConfig(...)
        
    Then in your config file, you can add it from the handlers namespace and add
    it to any logger you want::
    
        [handlers]
        keys=djangologdb
        
        [logger_root]
        level=NOTSET
        handlers=djangologdb
        
        [handler_djangologdb]
        class=handlers.DjangoDatabaseHandler
        args=()
        
    """
    def emit(self, record):
        from models import LogEntry

        try:
            LogEntry.objects.create_from_record(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

# Add the DjangoDatabaseHandler to the logging.handlers namespace.
logging.handlers.DjangoDatabaseHandler = DjangoDatabaseHandler

def add_handler(logger, handler):
    """
    Simple wrapper for `logging.addHandler` that prevents adding handlers twice.
    
    **Arguments**
    
    ``logger``
        The logger obtained via `logging.getLogger(...)`.
    
    ``handler``
        The handler instance. For example `DjangoDatabaseHandler()`.
    
    """
    already_registered = False

    for h in logger.handlers:
        if isinstance(h, handler.__class__):
            already_registered = True
            break

    if not already_registered:
        logger.addHandler(handler)
