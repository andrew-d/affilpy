import os
import sys
import logbook
import pkgutil

from furl import furl


class AffiliateLinkMgr(object):
    def __init__(self, config, debug=False):
        # Save config, registry.
        self.config = config
        self.registry = {}

        # Create logger.
        self.logger = logbook.Logger('AffiliateLinkMgr')

        # Load all modules.
        self._load_script_modules()
        # self.logger.debug("Registry is: %r" % (self.registry))


    def _get_registry(self, f):
        # Lower-case the host.
        host = f.host.lower()

        # Strip the "www." if it exists.
        if host.startswith('www.'):
            host = host[4:]

        # Try getting it.
        reg = self.registry.get(host)

        # self.logger.debug("Registry for '%s' is: %r" % (host, reg))
        return reg

    def detect_affiliate(self, url):
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
        reg = self._get_registry(f)
        if reg:
            is_affiliate, aff_id, _ = reg.detect(f)

            if is_affiliate:
                return {'affiliate_link': True, 'name': reg.NAME, 'id': aff_id}

        return {'affiliate_link': False}


    def strip_affiliate(self, url):
        """
        This function removes any affiliate links from a given URL.
        """
        f = furl(url)
        reg = self._get_registry(f)
        if not reg:
            return url

        is_affiliate, _, stripped = reg.detect(f)

        return str(stripped)


    def add_affiliate(self, url, strip=True, **kwargs):
        """
        This function will attempt to make a given link into an affiliate link.
        If the existing link is already an affiliate link, and the 'strip'
        parameter is given, the existing affiliate ID is removed.  Otherwise, this
        function will return the original link.
        """
        aff_info = self.detect_affiliate(url)
        if aff_info['affiliate_link']:
            if strip:
                self.logger.info("Stripping affiliate link")
                url = self.strip_affiliate(url)
            else:
                self.logger.info("Not stripping affiliate link")
                return url

        f = furl(url)
        reg = self._get_registry(f)
        if not reg:
            return url

        return str(reg.add(f, **kwargs))


    def _load_script_modules(self):
        our_dir = os.path.abspath(os.path.dirname(__file__))
        dirname = os.path.join(our_dir, 'sites')

        for filename in os.listdir(dirname):
            # Only load modules that are python files, and not our __init__.py
            name, ext = os.path.splitext(filename)
            if name == '__init__' or ext != '.py':
                continue

            # Import the module, and get it.
            # self.logger.debug("Importing module affilpy.sites.%s" % (name,))
            root_module = __import__('affilpy.sites', None, None, [name])
            module = getattr(root_module, name)

            # Get a logger for this plugin.
            child_logger = logbook.Logger('AffiliateLinkMgr - ' + name)

            # Instantiate any classes in the registry.
            for k, v in module.registry.items():
                if isinstance(v, type):
                    self.registry[k] = v(self.config, child_logger)


def make_linkshare_link(token, merchant_id, url):
    """
    This function makes building LinkShare links easier.
    """
    build_url = "http://getdeeplink.linksynergy.com/createcustomlink.shtml?token={token}&mid={mid}&murl={url}"

    req_url = build_url.format(token=token, mid=merchant_id, url=url)

    r = requests.get(req_url)
    if r.status is not 200:
        return None

    if not r.content.startswith('http'):
        return None

    return r.content
