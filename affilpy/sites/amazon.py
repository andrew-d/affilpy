import os
import re
import string

ASIN_RE = re.compile(r'[A-Za-z0-9]{10}')
ISBN_RE = re.compile(r'[0-9]{10}')  # Note: Amazon uses ISBN-10's

class AmazonLink(object):
    NAME = "Amazon"

    def __init__(self, config, logger):
        self.config = config
        self.log = logger

    def detect(self, f):
        # Default to "not an affiliate link"
        is_affiliate = False

        # Standard form: ?tag=affiliate_id
        aff_id = f.query.params.pop('tag', None)
        if aff_id:
            is_affiliate = True

        # Alternate form 1:
        #   http://www.amazon.com/dp/B004QGYPYQ/affiliate_id
        #   http://www.amazon.com/dp/B004QGYPYQ/ref=something/affiliate_id
        #   http://www.amazon.com/dp/0470088702/affiliate_id
        #   http://www.amazon.com/dp/0470088702/ref=something/affiliate_id
        #   http://amazon.com/exec/obidos/ASIN/whatever/aff_id
        #   http://amazon.com/exec/obidos/ASIN/whatever/ref=something/aff_id
        # Note that the bit after the "dp" is an ASIN or ISBN.
        # First, we find "dp".
        segments = f.path.segments
        lower_segments = map(string.lower, segments)
        marker_idx = None
        for seg in ['dp', 'asin', 'isbn']:
            try:
                marker_idx = lower_segments.index(seg)
            except ValueError:
                pass

        # If we found it, and if there are any segments afterwords...
        if marker_idx is not None and marker_idx + 1 < len(segments):
            # Check that the next segment is an ASIN or ISBN.  From Amazon, all
            # ASINs are 10-character alphanumeric.
            id_val = segments[marker_idx + 1]
            if ASIN_RE.match(id_val) or ISBN_RE.match(id_val):
                # This is an ASIN or ISBN, so it works.
                if marker_idx + 2 < len(segments):
                    removed_segments, segments = segments[marker_idx + 2:], segments[:marker_idx + 2]

                    # Re-add the last segment as blank.
                    segments.append('')

                    # Drop items from the beginning until we get something that
                    # doesn't look like "ref=something"
                    for item in removed_segments:
                        if len(item) > 0 and not item.lower().startswith('ref='):
                            aff_id = item
                            is_affiliate = True
                            break
                else:
                    # self.log.info("Valid ASIN/ISBN found, but there's nothing after it")
                    pass
            else:
                # self.log.info("Some ID found, but it's not an ASIN/ISBN: %r" % (id_val,))
                pass
        else:
            # self.log.info("'dp' segment found, but it's at the end")
            pass

        # Save segments if we're an affiliate link (i.e. if we've stripped things).
        if is_affiliate:
            f.path.segments = segments

        return is_affiliate, aff_id, f

    def add(self, f):
        f.query.params['tag'] = self.config[self.NAME]
        return f


# Load all Amazon TLDs from our data file.
dirname = os.path.abspath(os.path.dirname(__file__))
domain_path = os.path.join(dirname, "amazon_domains.txt")
domains = []
with open(domain_path, 'rb') as domain_file:
    for line in domain_file:
        if not line.startswith('#') and len(line) > 1:
            domains.append(line.lower().strip())

# Create the registry.
registry = {
    domain: AmazonLink for domain in domains
}

