# Ref: http://www.apple.com/itunes/affiliates/resources/documentation/linking-to-the-itunes-music-store.html#apps

class ItunesLink(object):
    NAME = "iTunes"

    def __init__(self, config, logger):
        self.config = config
        self.log = logger

    def detect(self, f):
        siteId = f.query.params.pop('siteID', None)
        f.query.params.pop('partnerId', None)
        return (siteId is not None), siteId, f

    def add(self, f):
        f.query.params['partnerId'] = self.config[self.NAME + "_partnerId"]
        f.query.params['siteID'] = self.config[self.NAME + "_siteID"]
        return f


registry = {
    "itunes.apple.com": ItunesLink
}

