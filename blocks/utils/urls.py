from django.conf import settings
import urlparse

def is_absolute_url(url):
	return bool(urlparse.urlparse(url).scheme)

def translate_url(url, locale=True):
    if locale and 'hvad' in settings.INSTALLED_APPS:
        p = url.split('/')
        p.pop(1)
        url = '/'.join(p)
    return url