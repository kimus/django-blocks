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
		print '%s.startswith(%s)' % (value, arg)
		return value.startswith(arg)
	else:
		return False


@register.assignment_tag(takes_context=True)
def blocks_menu(context, *args, **kwargs):
	from ..models import Menu
	from ..utils.urls import translate_url

	slug = kwargs.get('slug')
	keyword = kwargs.get('keyword')
	islist = kwargs.get('list', True)
	
	menu = None
	if slug and keyword:
		menu = Menu.objects.get(slug=slug, keyword=keyword)
	
	elif slug:
		menu =  Menu.objects.get(slug=slug)
	
	elif keyword:
		if keyword == 'BLOCKS_ROOT' or keyword == 'BLOCKS_EXACT':
			request = context.get('request')
			url = translate_url(request.path)
			try:
				m = Menu.objects.published(request).get(url__exact=url)
				parents = m.get_ancestors()
				if len(parents) == 0:
					root = m
				else:
					root = parents[0]

				print

				if keyword == 'BLOCKS_ROOT':
					menu = root
				elif keyword == 'BLOCKS_EXACT':
					menu = m
			except:
				pass
		else:
			menu =  Menu.objects.get(keyword=keyword)

	if menu:
		try:
			return menu.get_menus() if islist else menu
		except:
			pass
	
	return Menu.objects.filter(parent__isnull=True).exclude(type=Menu.TYPE_HIDDEN).order_by('tree_id')
