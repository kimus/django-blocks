from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from mptt.forms import MPTTAdminForm

from models import Page, Menu


class PageForm(forms.ModelForm):
	menu = forms.RegexField(label=_("URL"), max_length=100, regex=r'^[-\w/\.~]+$',
		help_text = _("Example: '/about/contact/'. Make sure to have leading"
					  " and trailing slashes."),
		error_message = _("This value must contain only letters, numbers,"
						  " dots, underscores, dashes, slashes or tildes."))

	class Meta:
		model = Page

	def clean_menu(self):
		menu = self.cleaned_data['menu']
		if not menu.startswith('/'):
			raise forms.ValidationError(ugettext("URL is missing a leading slash."))
		if (settings.APPEND_SLASH and
			'django.middleware.common.CommonMiddleware' in settings.MIDDLEWARE_CLASSES and
			not menu.endswith('/')):
			raise forms.ValidationError(ugettext("URL is missing a trailing slash."))
		return menu

	def clean(self):
		menu = self.cleaned_data.get('menu', '')
		is_relative = self.cleaned_data.get('is_relative', False)
		name = self.cleaned_data.get('name', '')
		sites = self.cleaned_data.get('sites', None)

		url = Page.get_url(menu, is_relative, name)		

		same_url = Page.objects.filter(url=url)
		if self.instance.pk:
			same_url = same_url.exclude(pk=self.instance.pk)

		if sites:
			if same_url.filter(sites__in=sites).exists():
				for site in sites:
					if same_url.filter(sites=site).exists():
						raise forms.ValidationError(
							_('Page with url %(url)s already exists for site %(site)s' %
							  {'url': url, 'site': site}))
		else:
			if same_url.exists():
				raise forms.ValidationError(
					_('Page with url %(url)s already exists for site %(site)s' %
					  {'url': url, 'site': '(empty)'}))


		return super(PageForm, self).clean()

