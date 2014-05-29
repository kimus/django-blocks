import django
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views import main
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, \
    					HttpResponseForbidden, HttpResponseNotFound, \
    					HttpResponseServerError
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, ugettext

from mptt.exceptions import InvalidMove
from mptt.forms import MPTTAdminForm

import json

from .models import Page, Menu


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



def _build_tree_structure(cls):
    """
    Build an in-memory representation of the item tree, trying to keep
    database accesses down to a minimum. The returned dictionary looks like
    this (as json dump):

    {"6": [7, 8, 10]
    "7": [12],
    "8": [],
    ...
    }
    """
    all_nodes = { }

    mptt_opts = cls._mptt_meta

    for p_id, parent_id in cls.objects.order_by(mptt_opts.tree_id_attr, mptt_opts.left_attr).values_list("pk", "%s_id" % mptt_opts.parent_attr):
        all_nodes[p_id] = []

        if parent_id:
            if not all_nodes.has_key(parent_id):
                # This happens very rarely, but protect against parents that
                # we have yet to iteratove over.
                all_nodes[parent_id] = []
            all_nodes[parent_id].append(p_id)

    return all_nodes



class ChangeList(main.ChangeList):
    """
    Custom ``ChangeList`` class which ensures that the tree entries are always
    ordered in depth-first order (order by ``tree_id``, ``lft``).
    """

    def __init__(self, request, *args, **kwargs):
        self.user = request.user
        super(ChangeList, self).__init__(request, *args, **kwargs)

    def get_query_set(self, *args, **kwargs):
        mptt_opts = self.model._mptt_meta
        return super(ChangeList, self).get_query_set(*args, **kwargs).order_by(mptt_opts.tree_id_attr, mptt_opts.left_attr)

    def get_results(self, request):
        mptt_opts = self.model._mptt_meta

        super(ChangeList, self).get_results(request)

        for item in self.result_list:
            item.item_is_editable = self.model_admin.has_change_permission(request, item)
            


class TreeEditor(admin.ModelAdmin):
    """
    The ``TreeEditor`` modifies the standard Django administration change list
    to a drag-drop enabled interface for django-mptt_-managed Django models.

    .. _django-mptt: https://github.com/django-mptt/django-mptt/
    """

    form = MPTTAdminForm

    def __init__(self, *args, **kwargs):
        super(TreeEditor, self).__init__(*args, **kwargs)

        self.list_display = list(self.list_display)

        if 'indented_short_title' not in self.list_display:
            if self.list_display[0] == 'action_checkbox':
                self.list_display[1] = 'indented_short_title'
            else:
                self.list_display[0] = 'indented_short_title'
        self.list_display_links = ('indented_short_title',)

        opts = self.model._meta
        self.change_list_template = [
            'admin/mptt/%s/%s/tree_editor.html' % (opts.app_label, opts.object_name.lower()),
            'admin/mptt/%s/tree_editor.html' % opts.app_label,
            'admin/mptt/tree_editor.html',
            ]

    def editable(self, item):
        return getattr(item, 'item_is_editable', True)

    def indented_short_title(self, item):
        """
        Generate a short title for an object, indent it depending on
        the object's depth in the hierarchy.
        """
        mptt_opts = item._mptt_meta
        r = ''
        try:
            url = item.get_absolute_url()
        except (AttributeError,):
            url = None

        if url:
            r = '<input type="hidden" class="medialibrary_file_path" value="%s" id="_refkey_%d" />' % (
                        url,
                        item.pk
                      )

        editable_class = ''
        if not self.editable(item):
            editable_class = ' tree-item-not-editable'

        level_indent = getattr(self, 'mptt_level_indent', 14)

        r += '<span id="page_marker-%d" class="page_marker%s" style="width: %dpx;">&nbsp;</span>&nbsp;' % (
                item.pk, editable_class, level_indent * (getattr(item, mptt_opts.level_attr) + 1))
        if hasattr(item, 'short_title') and callable(item.short_title):
            r += escape(item.short_title())
        else:
            r += escape(unicode(item))
        return mark_safe(r)
    indented_short_title.short_description = _('title')
    indented_short_title.allow_tags = True


    def _refresh_changelist_caches(self):
        """
        Refresh information used to show the changelist tree structure such as
        inherited active/inactive states etc.

        XXX: This is somewhat hacky, but since it's an internal method, so be it.
        """
        pass


    def get_changelist(self, request, **kwargs):
        return ChangeList

    def changelist_view(self, request, extra_context=None, *args, **kwargs):
        """
        Handle the changelist view, the django view for the model instances
        change list/actions page.
        """

        if 'actions_column' not in self.list_display:
            self.list_display.append('actions_column')

        # handle common AJAX requests
        if request.is_ajax():
            cmd = request.POST.get('__cmd')
            if cmd == 'move_node':
                return self._move_node(request)
            else:
                return HttpResponseBadRequest('Oops. AJAX request not understood.')

        self._refresh_changelist_caches()

        extra_context = extra_context or {}
        extra_context['tree_structure'] = mark_safe(json.dumps(
                                                    _build_tree_structure(self.model)))

        return super(TreeEditor, self).changelist_view(request, extra_context, *args, **kwargs)

    def has_change_permission(self, request, obj=None):
        """
        Implement a lookup for object level permissions. Basically the same as
        ModelAdmin.has_change_permission, but also passes the obj parameter in.
        """
        opts = self.opts
        r = request.user.has_perm(opts.app_label + '.' + opts.get_change_permission(), obj)
        return r and super(TreeEditor, self).has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        Implement a lookup for object level permissions. Basically the same as
        ModelAdmin.has_delete_permission, but also passes the obj parameter in.
        """
        opts = self.opts
        r = request.user.has_perm(opts.app_label + '.' + opts.get_delete_permission(), obj)
        return r and super(TreeEditor, self).has_delete_permission(request, obj)

    def _move_node(self, request):
        if hasattr(self.model.objects, 'move_node'):
            tree_manager = self.model.objects
        else:
            tree_manager = self.model._tree_manager

        cut_item = tree_manager.get(pk=request.POST.get('cut_item'))
        pasted_on = tree_manager.get(pk=request.POST.get('pasted_on'))
        position = request.POST.get('position')

        if position in ('last-child', 'left', 'right'):
            try:
                tree_manager.move_node(cut_item, pasted_on, position)
            except InvalidMove, e:
                self.message_user(request, unicode(e))
                return HttpResponse('FAIL')

            # Ensure that model save has been run
            cut_item = self.model.objects.get(pk=cut_item.pk)
            cut_item.save()

            self.message_user(request, ugettext('%s has been moved to a new position.') %
                cut_item)
            return HttpResponse('OK')

        self.message_user(request, ugettext('Did not understand moving instruction.'))
        return HttpResponse('FAIL')

    def _actions_column(self, instance):
        return ['<div class="drag_handle"></div>',]

    def actions_column(self, instance):
        return u' '.join(self._actions_column(instance))
    actions_column.allow_tags = True
    actions_column.short_description = _('move')

    def get_actions(self, request):
        actions = super(TreeEditor, self).get_actions(request)
        return actions


class MPTTTreeModelAdmin(TreeEditor):
    """
    A ModelAdmin to add changelist tree view and editing capabilities.
    Requires FeinCMS to be installed.
    """

    form = MPTTAdminForm

    def _actions_column(self, obj):
        actions = super(MPTTTreeModelAdmin, self)._actions_column(obj)
        # compatibility with Django 1.4 admin images (issue #191):
        # https://docs.djangoproject.com/en/1.4/releases/1.4/#django-contrib-admin
        if django.VERSION >= (1, 4):
            admin_img_prefix = "%sadmin/img/" % settings.STATIC_URL
        else:
            admin_img_prefix = "%simg/admin/" % settings.ADMIN_MEDIA_PREFIX
        return actions

    def get_actions(self, request):
        actions = super(MPTTTreeModelAdmin, self).get_actions(request)
        return actions