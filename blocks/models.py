from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.utils.timezone import now
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager

from hvad.models import TranslatableModel, TranslatedFields
#from hvad.manager import TranslationManager

from .managers import BaseManager, PublishableManager
from .utils.noconflict import classmaker
from .utils.urls import is_absolute_url
from .fields import SlugURLField, OrderField


class History(models.Model):
	def get_history(self):
		lst = []		
		try:
			lst = LogEntry.objects.filter(content_type=ContentType.objects.get_for_model(self).id, object_id=self.pk)
		except:
			pass
		return lst

	def get_creation(self):
		lst = self.get_history().order_by('action_time')
		return lst[0] if len(lst) > 0 else None

	def get_lastchange(self):
		lst = self.get_history()
		return lst.latest('action_time') if len(lst) > 0 else None

	def _get_creation_date(self):
		l = self.get_creation()
		return l.action_time if l is not None else None
	creation_date = property(_get_creation_date)

	def _get_creation_user(self):
		l = self.get_creation()
		return l.user if l is not None else None
	creation_user = property(_get_creation_user)

	def _get_lastchange_date(self):
		l = self.get_lastchange()
		return l.action_time if l is not None else None
	lastchange_date = property(_get_lastchange_date)

	def _get_lastchange_user(self):
		l = self.get_lastchange()
		return l.user if l is not None else None
	lastchange_user = property(_get_lastchange_user)

	class Meta:
		abstract = True


class SiteRelated(History):
	"""
	Abstract model for all things site-related. Adds a foreignkey to
	Django's ``Site`` model, and filters by site with all querysets.
	"""

	sites = models.ManyToManyField(Site, db_index=True)

	objects = models.Manager()
	on_site = CurrentSiteManager()

	class Meta:
		abstract = True

	def save(self, update_site=False, *args, **kwargs):
		"""
		Set the site to the current site when the record is first
		created, or the ``update_site`` argument is explicitly set
		to ``True``.
		"""
		if update_site or not self.id:
			super(SiteRelated, self).save(*args, **kwargs)
			current_site = Site.objects.get_current()
			self.sites.add(current_site)
		super(SiteRelated, self).save(*args, **kwargs)


class Orderable(models.Model):
	order = OrderField(verbose_name='', db_index=True, default=0, blank=True)

	class Meta:
		abstract = True
		ordering = ['order',]


class OrderableMPTTM(Orderable):

	objects = TreeManager()

	class Meta:
		abstract = True
		
	class MPTTMeta:
		order_insertion_by = ['order',]


class Publishable(SiteRelated):
	"""
	Abstract model that provides features of a visible content on the
	website such as publishing fields.
	"""

	status = models.IntegerField(_('status'),
		choices=PublishableManager.STATUS_CHOICES, default=PublishableManager.STATUS_DRAFT,
		help_text=_("With Draft chosen, will only be shown for admin users on the site."), 
		db_index=True)
	publish_date = models.DateTimeField(_('Published from'),
		help_text=_("With Published chosen, won't be shown until this time"),
		blank=True, null=True)
	expiry_date = models.DateTimeField(_('Expires on'),
		help_text=_("With Published chosen, won't be shown after this time"),
		blank=True, null=True)

	objects = PublishableManager()

	class Meta:
		abstract = True

	def save(self, *args, **kwargs):
		if self.publish_date is None:
			self.publish_date = now()
		super(Publishable, self).save(*args, **kwargs)


class Promotable(Publishable):
	promoted = models.BooleanField(_('promoted'))

	class Meta:
		abstract = True



class MultilingualTreeManager(TreeManager, PublishableManager):
	pass


class TranslatableMPTTModel(TranslatableModel, MPTTModel):
	__metaclass__ = classmaker()

	objects = MultilingualTreeManager()

	class Meta:
		abstract = True


class Menu(TranslatableMPTTModel, Publishable, OrderableMPTTM):
	name = models.CharField(_('name'), max_length=200)
	slug = SlugURLField(verbose_name=_('slug'), max_length=200, null=True, blank=True)
	url = models.CharField(verbose_name=_('url'), max_length=200, editable=False, db_index=True)
	parent = TreeForeignKey('self', verbose_name=_('parent menu'), related_name='children', null=True, blank=True)	
	
	TYPE_HIDDEN = 0
	TYPE_PAGE = 1
	TYPE_DYNAMIC = 2
	TYPE_LIST = 3
	TYPE_CHOICES = (
		(TYPE_PAGE, _("Page")),
		(TYPE_DYNAMIC, _("Dynamic")),
		(TYPE_LIST, _("List")),
		(TYPE_HIDDEN, _("Hidden")),
	)
	type = models.IntegerField(_('type'), choices=TYPE_CHOICES, default=TYPE_PAGE)
	keyword = models.CharField(_('keyword'), max_length=20, null=True, blank=True)

	translations = TranslatedFields(
		title = models.CharField(_('title'), max_length=80),
		description = models.TextField(_('description'), max_length=200, blank=True)
	)

	def type_image(self):
		return '<div class="blocks-icon blocks-type-%s" title="%s"></div>' % (self.get_type_display().lower(), self.get_type_display())
	type_image.allow_tags = True
	type_image.short_description = 'type'

	def short_title(self):
	    return self.name

	def title_with_spacer(self, spacer=u'...'):
		return (spacer * self.level) + u' ' + self.slug

	def get_menus(self):
		return self.get_children().exclude(type=Menu.TYPE_HIDDEN).order_by('lft')

	def get_pages(self):
		return Page.objects.published().filter(menu__exact=self.url, is_relative=True)

	def has_pages(self):
		return self.get_pages().count() > 0

	def has_children(self):
		return self.get_menus().count() > 0

	def has_children_or_pages(self):
		return self.has_children() or self.has_pages()

	def has_promotables(self):
		return self.get_promotables().count() > 0

	def get_promotables(self):
		leafs = list(self.get_leafnodes().values_list('url', flat=True)) + [self.url,]
		return Page.objects.filter(promoted=True, menu__in=leafs)


	class Meta(MPTTModel.Meta):
		verbose_name = _('menu')
		verbose_name_plural = _('menus')

	@staticmethod
	def fix_url(menu):
		if not is_absolute_url(menu.slug):
			menu.url = '/'
			if menu.parent:
				menu.url += menu.parent.url[1:]
			if menu.slug:
				menu.url += menu.slug + '/'
		else:			
			menu.url = menu.slug		

	def save(self, force_insert=False, force_update=False):
		old_url = self.url

		Menu.fix_url(self)

		super(Menu, self).save(force_insert, force_update)
		Menu.objects.rebuild()

		if self.url != old_url:
			# fix menus
			try:
				qs = Menu.objects.filter(parent=self)
				for m in qs:
					Menu.fix_url(m)
					m.save()
			except Menu.DoesNotExist:
				pass

			# fix pages
			try:
				qs = Page.objects.filter(menu=old_url)
				for p in qs:
					p.menu = self.url
					p.url = Page.get_url(self.url, p.is_relative, p.name)
					p.save()
			except Page.DoesNotExist:
				pass

	def __unicode__(self):
		return u'%s -- %s' % (self.url, self.title)

	#@models.permalink
	def get_absolute_url(self):
		return self.url


class Template(History):
	name = models.CharField(_('name'), max_length=80)
	template = models.CharField(_('template'), max_length=200)

	def __init__(self, *args, **kwargs):		
		super(Template, self).__init__(*args, **kwargs)
		self.old_template = self.template

	def save(self, force_insert=False, force_update=False):
		super(Template, self).save(force_insert, force_update)
		if self.template != self.old_template:
			try:
				qs = Page.objects.filter(template_name=self.old_template)
				for p in qs:
					p.template_name = self.template
					p.save()
			except Page.DoesNotExist:
				pass

	def __unicode__(self):
		return '%s' % self.name


class Page(TranslatableModel, Promotable, Orderable):
	name = models.CharField(_('name'), max_length=200)
	menu = models.CharField(_('url'), max_length=200)
	url = models.CharField(verbose_name=_('url'), max_length=200, unique=True, editable=False, db_index=True)
	template_name = models.CharField(_('template name'), max_length=70, blank=True)
	is_relative = models.BooleanField(_('relative'),
		help_text=_("If a page is relative then the page slug (normalized name) is appended to the url."))

	translations = TranslatedFields(
		title = models.CharField(_('title'), max_length=200),
		content = models.TextField(_('content'), blank=True)
	)

	objects = PublishableManager()

	class Meta:
		ordering = ['url','order',]

	def get_type_display(self):
		if self.is_relative:
			return 'Relative'
		else:
			return 'Index'

	def type_image(self):
		return '<div class="blocks-icon blocks-page-%s" title="%s"></div>' % (self.get_type_display().lower(), self.get_type_display())
	type_image.allow_tags = True
	type_image.short_description = 'type'

	@staticmethod
	def get_url(menu, is_relative, name):
		url = menu
		if is_relative:
			url += slugify(name) + '/'
		return url

	def save(self, force_insert=False, force_update=False):
		self.url = Page.get_url(self.menu, self.is_relative, self.name)
		super(Page, self).save(force_insert, force_update)

	def __unicode__(self):
		return u'%s -- %s' % (self.url, self.name)
		
	def __str__(self):
		return "%s -- %s" % (self.url, self.name)

	@models.permalink
	def get_absolute_url(self):
		return ('blocks_page', (), {'url': self.url[1:] })

	@property
	def lead(self):
		pos = self.content.find('</p>')
		if pos != -1:
			return mark_safe(self.content[:pos + 4])
		return mark_safe(self.content)

	@property
	def body(self):
		pos = self.content.find('</p>')
		if pos != -1:
			return mark_safe(self.content[pos + 4:])
		return ''
