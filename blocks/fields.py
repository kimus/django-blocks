from django.db import models
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from sorl.thumbnail import ImageField as SorlImageField

from .utils.urls import is_absolute_url

class SlugURLValidator(object):
	message = _('Enter a valid value.')
	code = 'invalid'

	def __init__(self, arg1):
		pass

	def __call__(self, value):
		try:
			if not is_absolute_url(value):
				value.index('/')
				raise ValidationError(self.message, code=self.code)
		except ValueError:
			pass


class SlugURLField(models.CharField):
	default_validators = [SlugURLValidator]


class ImageField(SorlImageField):
	pass


class HiddenFormField(forms.IntegerField):
	def __init__(self, *args, **kwargs):
		kwargs['widget'] = forms.HiddenInput
		super(HiddenFormField, self).__init__(*args, **kwargs)

class OrderField(models.PositiveSmallIntegerField):
	def formfield(self, **kwargs):
		defaults = {'form_class': HiddenFormField}
		defaults.update(kwargs)
		return super(OrderField, self).formfield(**defaults)