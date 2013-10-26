from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import get_language


register = template.Library()


@register.simple_tag
def site_url(site_id):
	try:
		site = Site.objects.get(id=site_id)
	except Site.DoesNotExist:
		site = Site.objects.get_current()
	return "//%s" % site.domain


@register.filter
def urlmatchwith(value, arg):
	url = ''
	if 'django.middleware.locale.LocaleMiddleware' in settings.MIDDLEWARE_CLASSES:
		url = '/' + get_language()
	url += arg
	if arg == '/':
		return value == url
	else:
		return startswith(value, url)


@register.filter
def startswith(value, arg):
	"""Usage, {% if value|startswith:"arg" %}"""
	if isinstance(value, str) or isinstance(value, unicode):
		return value.startswith(arg)
	else:
		return False


@register.assignment_tag
def blocks_menu(*args, **kwargs):
	from ..models import Menu
	slug = kwargs.get('slug')
	keyword = kwargs.get('keyword')
	
	qs = None
	if slug and keyword:
		qs = Menu.objects.filter(slug=slug, keyword=keyword)
	elif slug:
		qs =  Menu.objects.filter(slug=slug)
	elif keyword:
		qs =  Menu.objects.filter(keyword=keyword)

	if qs:
		try:
			menu = qs.get()			
			return menu.get_menus()
		except:
			pass
	
	return Menu.objects.filter(parent__isnull=True).exclude(type=Menu.TYPE_HIDDEN).order_by('tree_id')
