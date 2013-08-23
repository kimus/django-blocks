from django.conf.urls import patterns, url

urlpatterns = patterns('blocks.views',
	url(r'^pages_link_list/$', 'pages_link_list'),
    (r'^(?P<url>.*)$', 'page'),
)
