from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.core.xheaders import populate_xheaders
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.template import loader, RequestContext
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect

from .models import Page


DEFAULT_TEMPLATE = 'pages/default.html'

# This view is called from PageFallbackMiddleware.process_response
# when a 404 is raised, which often means CsrfViewMiddleware.process_view
# has not been called even if CsrfViewMiddleware is installed. So we need
# to use @csrf_protect, in case the template needs {% csrf_token %}.
# However, we can't just wrap this view; if no matching page exists,
# or a redirect is required for authentication, the 404 needs to be returned
# without any CSRF checks. Therefore, we only
# CSRF protect the internal implementation.
def page(request, url, locale=False):
    if not url.startswith('/'):
        url = '/' + url
    site_id = get_current_site(request).id    
    if locale and 'hvad' in settings.INSTALLED_APPS:
        p = url.split('/')
        p.pop(1)
        url = '/'.join(p)
    try:
        f = get_object_or_404(Page, url__exact=url, sites__id__exact=site_id)
    except Http404:
        if not url.endswith('/') and settings.APPEND_SLASH:
            url += '/'
            f = get_object_or_404(Page, url__exact=url, sites__id__exact=site_id)
            return HttpResponsePermanentRedirect('%s/' % request.path)
        else:
            raise
    return render_page(request, f)

@csrf_protect
def render_page(request, f):
    """
    Internal interface to the flat page view.
    """
    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    #if f.registration_required and not request.user.is_authenticated():
    #    from django.contrib.auth.views import redirect_to_login
    #    return redirect_to_login(request.path)
    if f.template_name:
        t = loader.select_template((f.template_name, DEFAULT_TEMPLATE))
    else:
        t = loader.get_template(DEFAULT_TEMPLATE)

    # To avoid having to always use the "|safe" filter in page templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    f.title = mark_safe(f.title)
    f.content = mark_safe(f.content)

    c = RequestContext(request, {
        'page': f,
    })
    response = HttpResponse(t.render(c))
    populate_xheaders(request, response, Page, f.id)
    return response


def pages_link_list(request):
    """
    Returns a HttpResponse whose content is a Javscript file representing a
    list of links to flatpages.
    """
    from tinymce.views import render_to_link_list
    link_list = [(page.title, page.url) for page in Page.objects.all()]
    return render_to_link_list(link_list)