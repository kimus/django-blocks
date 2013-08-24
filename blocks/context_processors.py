from django.utils.translation import get_language

from .models import Menu


def common(request):
    return {
    	'BLOCKS_MENUS': Menu.objects.published(request).filter(parent__isnull=True).order_by('tree_id'),
    	'BLOCKS_LANGUAGE': get_language()
    }