django-blocks
=============

An easier way to build Web apps like an blog or CMS more quickly and with almost no code


Quick start
-----------

1. Add "blocks" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'blocks',
    )

2. Include the blocks URLconf in your project urls.py like this::

urlpatterns += i18n_patterns('',
	url('', include('blocks.urls')),
)

3. Run `python manage.py migrate` to create the blocks models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a menu or page (you'll need the Admin app enabled).
