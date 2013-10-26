from django.utils.translation import get_language

from .utils.urls import translate_url
from .models import Menu


def common(request):
	url = translate_url(request.path)
	qs = Menu.objects.published(request)
	return {
		'BLOCKS_MENUS': qs.filter(parent__isnull=True).exclude(type=Menu.TYPE_HIDDEN).order_by('tree_id'),
		#'BLOCKS_MENU_ROOT': qs.filter(url__startswith=url),
		#'BLOCKS_MENU_EXACT': qs.get(url__exact=url),
		'BLOCKS_LANGUAGE': get_language()
	}