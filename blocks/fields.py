from django.db import models
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from sorl.thumbnail import ImageField as SorlImageField

from .utils.urls import is_absolute_url

import os
from uuid import uuid4


class SlugURLValidator(object):
	message = _("Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.")
	code = 'invalid'

	def __init__(self):
		pass

	def __call__(self, value):
		try:
			if not is_absolute_url(value):
				value.index('/')
				raise ValidationError(self.message, code=self.code)
		except ValueError:
			pass

blocks_validator_slug = SlugURLValidator()

class SlugURLField(models.CharField):
	default_validators = [blocks_validator_slug]

	def validate(self, value, model_instance):
		from .models import Menu

		if isinstance(model_instance, Menu):
			self.validators = []
			if model_instance.type != Menu.TYPE_REDIRECT:
				self.validators.append(blocks_validator_slug)

		super(SlugURLField, self).validate(value, model_instance)

	def to_python(self, value):
		value = super(SlugURLField, self).to_python(value)
		if value is None:
			return value
		if not is_absolute_url(value):
			value = value.lower()
		return value


class ImageField(SorlImageField):
#class ImageField(models.ImageField):
	def __init__(self, verbose_name=None, name=None, upload_to=None, storage=None, **kwargs):
		if not callable(upload_to):
			upload_to = ImageField.path_and_rename(upload_to)
		super(ImageField, self).__init__(verbose_name=verbose_name, name=name, upload_to=upload_to, storage=storage, **kwargs)

	@staticmethod
	def path_and_rename(path):
		def wrapper(instance, filename):
			ext = filename.split('.')[-1]
			
			# set filename as random string
			filename = '{}.{}'.format(uuid4().hex, ext)

			# return the whole path to the file
			return os.path.join('uploads', path, instance.__class__.__name__.lower(), filename)
		return wrapper


class HiddenFormField(forms.IntegerField):
	def __init__(self, *args, **kwargs):
		kwargs['widget'] = forms.HiddenInput
		super(HiddenFormField, self).__init__(*args, **kwargs)


class OrderField(models.PositiveSmallIntegerField):
	def formfield(self, **kwargs):
		defaults = {'form_class': HiddenFormField}
		defaults.update(kwargs)
		return super(OrderField, self).formfield(**defaults)

try:
	from south.modelsinspector import add_introspection_rules
	add_introspection_rules([], ["^blocks\.fields\.SlugURLField"])
	add_introspection_rules([], ["^blocks\.fields\.ImageField"])
	add_introspection_rules([], ["^blocks\.fields\.OrderField"])
except:
	pass