from furl import furl
import requests

class LinkShareLink(object):
    NAME = "LinkShare"

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def detect(self, f):
        orig_url = f.query.params.get("RD_PARM1")
        if orig_url is not None:
            # We could get the original URL.
            ret_url = furl(orig_url)
        else:
            ret_url = f

        # Try and detect the ID.
        id = f.query.params.get('id')
        return (id is not None), id, ret_url

    def add(self, f):
        raise NotImplementedError("Cannot create LinkShare links with this API")

registry = {
    "click.linksynergy.com": LinkShareLink
}

