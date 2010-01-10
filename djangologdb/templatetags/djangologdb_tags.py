from django.template import Library

register = Library()

def djangologdb_media_url():
    """
    Returns the string contained in the setting ADMIN_MEDIA_PREFIX.
    """
    try:
        from djangologdb import settings as djangologdb_settings
    except:
        return ''
    return djangologdb_settings.MEDIA_URL
djangologdb_media_url = register.simple_tag(djangologdb_media_url)

