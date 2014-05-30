#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
	name = "django-blocks",
	version = "1.0",

	packages = find_packages(),

	author = "Helder Rossa",
	author_email = "kimus.linuxus@gmail.com",
	description = "An easier way to build Web apps more quickly and with almost no code.",
	license = "MIT License",
	url = "https://github.com/kimus/django-blocks",

	classifiers = ['Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
		'Topic :: Software Development',
		'Topic :: Software Development :: Libraries :: Application Frameworks',
	],
)
