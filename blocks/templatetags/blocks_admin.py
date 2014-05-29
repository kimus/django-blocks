from django import template
from django.conf import settings

register = template.Library()


@register.assignment_tag
def get_language_byindex(index):
	lang = ('', '')
	try:
		lang = settings.LANGUAGES[index]
	except KeyError:
		pass
	except IndexError:
		pass
	return lang
