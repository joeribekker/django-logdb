CHANGES
=======

pre-0.9.6
---------

- Updated README to include examples to serve the media.
- Fixed a bug where objects/instances were pickled too deep. Log record 
  arguments and the extra parameters are now stringified to prevent this.

0.9.5
-----
- Removed Django as a requirement (although it's still required) to prevent
  conflicts with djangorecipe.

0.9.4
-----
- Fixed manifest to include changes.

0.9.3
-----
- Added template for LogEntry view.
- Renamed templates to Django's default. You can still override them.

0.9.2
-----
- Initial release on PyPI.