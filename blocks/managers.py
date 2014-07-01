from django.db.models import Manager, Q
from django.utils.translation import ugettext_lazy as _
from django.db.models.query import QuerySet
from django.utils.translation import get_language, activate
from django.conf import settings

from hvad.manager import TranslationManager

from datetime import datetime


def isvalidlanguage(lang):
	found = False
	for k,v in settings.LANGUAGES:
		if k == lang:
			found = True
			break
	return found

if settings.LANGUAGE_CODE != get_language() and not isvalidlanguage(get_language()):
	activate(settings.LANGUAGE_CODE)

class BaseManager(TranslationManager):
	def translated(self):
		qs = self.model.objects
		try:
			getattr(self.model.objects, 'language')
			lang = get_language()
			if not isvalidlanguage(lang):
				lang = settings.LANGUAGE_CODE
			if not isvalidlanguage(lang) and len(settings.LANGUAGES) > 0:
				lang = settings.LANGUAGES[0][0]
			qs = qs.language(lang)
		except AttributeError:
			pass
		return qs

class PublishableManager(BaseManager):

	STATUS_DRAFT = 1
	STATUS_PUBLISHED = 2,
	STATUS_DISABLED = 3
	STATUS_CHOICES = (
		(STATUS_DRAFT, _("Draft")),
		(STATUS_PUBLISHED, _("Published")),
		(STATUS_DISABLED, _("Disabled")),
	)

	def published(self, request=None):
		# allow staff users to preview pages
		allow_unpublished  = (request and hasattr(request, 'user') and request.user.is_authenticated() and request.user.is_staff)	
		if allow_unpublished:
			return self.translated()
		else:
			return self.translated().filter(
				Q(expiry_date__gte=datetime.now()) | Q(expiry_date__isnull=True),
				publish_date__lte=datetime.now(),
				status=PublishableManager.STATUS_PUBLISHED
			)


class PromotableManager(PublishableManager):
	def promoted(self):
		return self.published().filter(promoted=True)
