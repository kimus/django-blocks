#!/usr/bin/env python
import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
	name = "django-blocks",
	version = "1.0",

	packages = ['blocks'],
	include_package_data=True,

	author = "Helder Rossa",
	author_email = "kimus.linuxus@gmail.com",
	description = "An easier way to build Web apps more quickly and with almost no code.",
	long_description=README,
	
	license = "MIT License",
	url = "https://github.com/kimus/django-blocks",

	platform="any",

	classifiers = [
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
