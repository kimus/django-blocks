import urlparse

def is_absolute_url(url):
	return bool(urlparse.urlparse(url).scheme)
