import os
import sys
import pkgutil

from furl import furl

# This is our registry of hostnames.
REGISTRY = {}


def _get_registry(f):
    # Lower-case the host.
    host = f.host.lower()

    # Strip the "www." if it exists.
    if host.startswith('www.'):
        host = host[4:]

    # Try getting it.
    return REGISTRY.get(host)


def detect_affiliate(url):
    """
    This function detects affiliate links on the given URL.  It will return any
    affiliate links found in the form of a dictionary:
        >>> detect_affiliate('http://www.amazon.com/dp/ASIN/?tag=Affiliate_ID')
        {'affiliate_link': True, 'affiliates': [{'name': 'Amazon', 'id': 'Affiliate_ID'}]}
    If the given link is not an affiliate link, it will return:
        >>> detect_affiliate('http://www.othersite.com/')
        {'affiliate_link': False, 'affiliates': []}
    """

    f = furl(url)
    reg = _get_registry(f)
    if not reg:
        return False

    aff_ids, _ = reg.detect(f)

    if len(aff_ids) > 0:
        return {'affilite_link': True, 'affiliates': [
            {'name': reg.NAME, 'id': i} for i in aff_ids
        ]}
    else:
        return {'affilite_link': False, 'affiliates': []}


def strip_affiliate(url):
    """
    This function removes any affiliate links from a given URL.
    """
    f = furl(url)
    reg = _get_registry(f)
    if not reg:
        return url

    _, stripped = reg.detect(f)

    return str(stripped)


def add_affiliate(url, strip=True):
    """
    This function will attempt to make a given link into an affiliate link.
    If the existing link is already an affiliate link, and the 'strip'
    parameter is given, the existing affiliate ID is removed.  Otherwise, this
    function will return the original link.
    """
    aff_info = detect_affiliate(url)
    if aff_info['affilite_link']:
        if strip:
            url = strip_affiliate(url)
        else:
            return url

    f = furl(url)
    reg = _get_registry(f)
    if not reg:
        return url

    return str(reg.add(f))


def load_script_modules():
    our_dir = os.path.abspath(os.path.dirname(__file__))
    dirname = os.path.join(our_dir, 'sites')

    for filename in pkgutil.iter_modules(dirname):
        # Only load modules that are python files, and not our __init__.py
        name, ext = os.path.splitext(filename)
        if name == '__init__' or ext != '.py':
            continue

        # Import the module, and get it.
        root_module = __import__('affilpy.sites', None, None, [name])
        module = getattr(root_module, name)

        # Instantiate any classes in the registry.
        reg = module.registry
        for k, v in reg.items():
            if isinstance(v, type):
                reg[k] = v()

        # Save in global registry.
        REGISTRY.update(reg)


# Load all modules.
load_script_modules()

