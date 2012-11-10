
class SmashwordsLink(object):
    NAME = "Smashwords"

    def __init__(self, config, logger):
        self.config = config
        self.log = logger

    def detect(self, f):
        id = f.query.params.pop('ref', None)
        return (id is not None), id, f

    def add(self, f):
        f.query.params['ref'] = self.config[self.NAME]
        return f


registry = {
    'smashwords.com': SmashwordsLink
}
