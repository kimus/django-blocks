from models import Menu

def common(request):
    return {
    	'menu_items': Menu.objects.filter(parent__isnull=True)
    }