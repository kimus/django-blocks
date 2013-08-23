from django.contrib import admin
from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.options import ModelAdmin
from django.conf import settings

from tinymce.widgets import TinyMCE
from mptt_tree.forms import MPTTTreeModelAdmin
from sorl.thumbnail.admin import AdminImageMixin

from .forms import PageForm
from .models import Menu, MenuTranslation, Template, Page, PageTranslation

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


class TranslationsInline(admin.StackedInline):
	template = 'admin/blocks/edit_inline/translatable.html'
	max_num = len(settings.LANGUAGES)
	extra = len(settings.LANGUAGES)


class MenuTranslationInline(TranslationsInline):
	model = MenuTranslation


class MenuAdmin(MPTTTreeModelAdmin):
	inlines = [MenuTranslationInline,]

	fieldsets = (
		(None, {'fields': ('slug', 'parent', )}),
		PUBLISHABLE_OPTIONS,
	)
	list_display = ('name', 'url', 'creation_user', 'lastchange_date')
	search_fields = ['slug', 'url']

	#exclude = ('url',)
	#prepopulated_fields = {'slug':('title',),}
	#list_editable = ('order',)
	sortable = 'order'

	mptt_level_indent = 20

	#def get_changelist_form(self, request, **kwargs):
	#	kwargs.setdefault('form', OrderableMenuForm)
	#	return super(MenuAdmin, self).get_changelist_form(request, **kwargs)

admin.site.register(Menu, MenuAdmin)


class TemplateAdmin(ModelAdmin):
	list_display = ('name', 'template', 'creation_user', 'lastchange_date')
	search_fields = ['name', 'template']

admin.site.register(Template, TemplateAdmin)


def get_menus_choices():
	def _get_next(item):
		items = ()
		for m in item.children.all():
			items += (( m.url, m.title_with_spacer(spacer=u'. . . ') ),)
			items += _get_next(m)
		return items
	items = ()
	menus = Menu.objects.filter(parent__isnull=True)
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
		PUBLISHABLE_OPTIONS,
	)
	list_display = ('name', 'url', 'template_name', 'creation_user', 'lastchange_date')
	search_fields = ['name', 'url']
	#list_filter = ('sites',)
	#filter_horizontal = ('sites',)

	form = PageForm

	def formfield_for_dbfield(self, db_field, **kwargs):
		#if db_field.name == 'content':
		#	return forms.CharField(widget=TinyMCE(
		#		attrs={'cols': 80, 'rows': 30},
		#		mce_attrs={'external_link_list_url': reverse('tinymce.views.flatpages_link_list')},
		#	))
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