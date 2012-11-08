import re

ASIN_RE = re.compile(r'[A-Za-z0-9]{10}')

class AmazonLink(object):
    NAME = "Amazon"

    def detect(self, f):
        aff_ids = []

        # Standard form: ?tag=affiliate_id
        aff = f.query.params.get('tag')
        if aff:
            aff_ids.append(aff)

        # Alternate form: appending affiliate_id after the /ASIN/whatever/ segment.
        # First, we find "asin".
        lower_segments = map(lambda s: s.lower(), f.path.segments)
        try:
            asin_index = lower_segments.index('asin')
        except ValueError:
            asin_index = None

        # If we found it, and if there are any segments afterwords...
        if asin_index and asin_index + 1 < len(f.path.segments):
            # Check that the next segment is an ASIN.  From Amazon, all
            # ASINs are 10-character alphanumeric.
            asin = f.path.segments[asin_index + 1]
            if ASIN_RE.match(asin):
                # Good, we have the asin.  If there's another segment
                # after this, we strip it.
                if asin_index + 2 < len(f.path.segments):
                    aff = f.path.segments.remove(asin_index + 2)
                    if aff:
                        aff_ids.append(aff)

        # TODO: investigate the style:
        #   http://amazon.com/exec/obidos/ASIN/whatever/ref=something/aff_id
        return aff_ids, f

    def add(self, f):
        f.query.params['tag'] = 'affilliate_id'
        return f


registry = {
    'amazon.com': AmazonLink,
    'amazon.co.uk': AmazonLink,
}

