from django.contrib import admin
from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.options import ModelAdmin
from django.conf import settings
from django.forms.models import BaseInlineFormSet

from tinymce.widgets import TinyMCE
from mptt_tree.forms import MPTTTreeModelAdmin
from sorl.thumbnail.admin import AdminImageMixin
from datetime import datetime

from .forms import PageForm
from .models import Menu, MenuTranslation, Template, Page, PageTranslation
from .managers import PublishableManager


def make_published(modeladmin, request, queryset):
	queryset.update(status=PublishableManager.STATUS_PUBLISHED, publish_date=datetime.now())
make_published.short_description = _('Mark selected as Published')


def make_unpublished(modeladmin, request, queryset):
	queryset.update(status=PublishableManager.STATUS_DRAFT, publish_date=None)
make_unpublished.short_description = _('Mark selected as Unpublished (Draft)')


def make_promoted(modeladmin, request, queryset):
	queryset.update(promoted=True)
make_promoted.short_description = _('Mark selected as Promoted')


def make_unpromoted(modeladmin, request, queryset):
	queryset.update(promoted=False)
make_unpromoted.short_description = _('Mark selected as Unpromoted')


actions_published = [make_published, make_unpublished]
actions_promoted = actions_published + [make_promoted, make_unpromoted]


PUBLISHABLE_OPTIONS = (
	_('Publishing Options'), {
		'fields': ('publish_date', 'expiry_date', 'status',), 
		'classes': ('grp-collapse grp-closed', )
	})

PROMOTABLE_OPTIONS = (
	_('Publishing Options'), {
		'fields': ('publish_date', 'expiry_date', 'promoted', 'status',), 
		'classes': ('grp-collapse grp-closed', )
	})


class ImageTabularInline(AdminImageMixin, admin.TabularInline):
    pass

class ImageStackedInline(AdminImageMixin, admin.StackedInline):
    pass


class TranslationsInlineFormSet(BaseInlineFormSet):
	def clean(self):
		"""if only the default language is filled then copy default language to others"""
		lastdata = None
		for form in self.forms:
			if not hasattr(form, 'cleaned_data'):
				continue
			data = form.cleaned_data
			count = 0
			for d in data:				
				v = data[d]
				if v != None and v != u'':
					count += 1
			if count <= 3 and lastdata != None:
				for k in lastdata:
					if k != 'master' and k != 'language_code' and k != 'id' and k != 'DELETE':
						key = "%s-%s" % (form.prefix, k)
						form.data[key] = lastdata.get(k)
				form.full_clean()
			else:
				lastdata = data
		super(TranslationsInlineFormSet, self).clean()

class TranslationsInline(admin.StackedInline):
	template = 'admin/blocks/edit_inline/translatable.html'
	max_num = len(settings.LANGUAGES)
	extra = len(settings.LANGUAGES)
	formset = TranslationsInlineFormSet


class MenuTranslationInline(TranslationsInline):
	model = MenuTranslation


class MenuAdmin(MPTTTreeModelAdmin):
	inlines = [MenuTranslationInline,]

	fieldsets = (
		(None, {'fields': ('name', 'slug', 'parent', )}),
		(
		_('Publishing Options'), {
			'fields': ('publish_date', 'expiry_date', 'type', 'keyword', 'status',), 
			'classes': ('grp-collapse grp-closed', )
		})
	)
	list_display = ('actions_column', 'type_image', 'indented_short_title', 'url', 'creation_user', 'lastchange_date', 'status')
	search_fields = ['name', 'slug', 'keyword']
	list_filter = ('type', 'status', 'keyword')
	sortable = 'order'
	mptt_level_indent = 20
	#indented_short_title = _('name')
	prepopulated_fields = {'slug':('name',)}
	actions = actions_published

admin.site.register(Menu, MenuAdmin)


class TemplateAdmin(ModelAdmin):
	list_display = ('name', 'template', 'creation_user', 'lastchange_date')
	search_fields = ['name', 'template']

admin.site.register(Template, TemplateAdmin)


def get_menus_choices():
	def _get_next(item):
		items = ()
		for m in item.children.exclude(type__in=[Menu.TYPE_REDIRECT,]):
			items += (( m.url, m.title_with_spacer(spacer=u'. . . ') ),)
			items += _get_next(m)
		return items
	items = ()
	menus = Menu.objects.filter(parent__isnull=True).exclude(type__in=[Menu.TYPE_DYNAMIC, Menu.TYPE_REDIRECT])
	for m in menus:
		items += (( m.url, m.title ),)
		items += _get_next(m)
	return items

def get_templates_choices():
	items = ()
	templates = Template.objects.all()
	for m in templates:
		items += (( m.template, m.name ),)
	return items


class PageTranslationInline(TranslationsInline):
	model = PageTranslation
	def formfield_for_dbfield(self, db_field, **kwargs):
		if db_field.name == 'content':
			return forms.CharField(widget=TinyMCE(
				attrs={'cols': 80, 'rows': 30, 'height': 200},
				mce_attrs={'external_link_list_url': reverse('blocks.views.pages_link_list')},
			))
		return super(PageTranslationInline, self).formfield_for_dbfield(db_field, **kwargs)

class PageAdmin(ModelAdmin):
	inlines = [PageTranslationInline,]

	fieldsets = (
		(None, {'fields': ('name', 'menu', 'is_relative', 'template_name')}),
		(_('Publishing Options'), {
			'fields': ('publish_date', 'expiry_date', 'keyword', 'order', 'promoted', 'status',), 
			'classes': ('grp-collapse grp-closed', )
		})
	)
	list_display = ('type_image', 'name', 'url', 'creation_user', 'lastchange_date', 'status', 'promoted')
	list_display_links = ('name', )
	search_fields = ['name', 'url', 'keyword']
	list_filter = ('status', 'promoted', 'keyword', 'template_name')
	actions = actions_promoted
	form = PageForm	

	def formfield_for_dbfield(self, db_field, **kwargs):
		if db_field.name == 'order':
			return forms.ChoiceField(choices=(('', ''),) + tuple((i, i) for i in range(0, 31)), required=True, initial=0)
		if db_field.name == 'template_name':
			return forms.ChoiceField(choices=get_templates_choices())
		return super(PageAdmin, self).formfield_for_dbfield(db_field, **kwargs)
		
	def get_form(self, request, obj=None, **kwargs):
		from django.forms import ChoiceField
		form = super(PageAdmin, self).get_form(request, obj, **kwargs)
		f = form.base_fields['menu']
		form.base_fields['menu'] = forms.ChoiceField(label=f.label, choices=get_menus_choices())
		return form

admin.site.register(Page, PageAdmin)