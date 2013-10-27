from django.utils.translation import get_language

from .utils.urls import translate_url
from .models import Menu


def common(request):
	qs = Menu.objects.published(request)
	return {
		'BLOCKS_MENUS': qs.filter(parent__isnull=True).exclude(type=Menu.TYPE_HIDDEN).order_by('tree_id'),
		'BLOCKS_LANGUAGE': get_language(),
		'BLOCKS_FULL_URL': translate_url(request.path)
	}