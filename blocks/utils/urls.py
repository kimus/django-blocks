from django.conf import settings
from django.utils.translation import get_language
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
		if len(p) > 1:
			l = p.pop(1)
			langs = [i[0] for i in settings.LANGUAGES]
			if l in langs:
				url = '/'.join(p)
	return url


def get_menu_absolute_url(url, locale=True):
	if is_absolute_url(url):
		return url
	return '/%s%s' % (get_language(), url)