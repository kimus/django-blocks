from django.conf import settings
import urlparse

def get_menu_url(keyword, default=None):
	from blocks.models import Menu
	url = ''
	try:
		url = Menu.objects.get(keyword=keyword).url
	except:
		if default:
			url = '/' + default + '/'
	return url

def is_absolute_url(url):
	return bool(urlparse.urlparse(url).scheme)

def translate_url(url, locale=True):
    if locale and 'hvad' in settings.INSTALLED_APPS:
        p = url.split('/')
        l = p.pop(1)
        langs = [i[0] for i in settings.LANGUAGES]
        if l in langs:
        	url = '/'.join(p)
    return url