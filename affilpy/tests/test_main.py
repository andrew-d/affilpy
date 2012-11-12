from __future__ import print_function

import os
import yaml
import unittest

from affilpy import AffiliateLinkMgr
from .helpers import BaseTestCase, parametrize, parameters

dir_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(dir_path, 'detect_strip_tests.yaml'), 'rb') as f:
    data = f.read()
detect_strip_test_data = list(yaml.load_all(data))

with open(os.path.join(dir_path, 'add_tests.yaml'), 'rb') as f:
    data = f.read()
add_test_data = list(yaml.load_all(data))


def generate_name(idx, data):
    if data is not None:
        return data['test_name']
    else:
        return "test_" + str(idx)


@parametrize
class TestAffiliateEngines(BaseTestCase):
    def setup(self):
        self.config = {}
        self.a = AffiliateLinkMgr(self.config)

    @parameters(detect_strip_test_data, name_func=generate_name)
    def test_detect_and_strip(self, data):
        if data is None:
            return

        affil_name = data['affil_name']
        urls = data['urls']
        id   = data['id']
        is_affiliate = data['is_affiliate']
        stripped_test = data.get('stripped_url')

        # Test detecting affiliate links.
        for url in urls:
            # Detect affiliate links, check to ensure our value matches.
            detect = self.a.detect_affiliate(url)
            self.assert_equal(detect['affiliate_link'], is_affiliate)

            # If this is an affiliate link, check more.
            if is_affiliate:
                # Name/ID checking.
                self.assert_equal(detect['name'], affil_name)
                self.assert_equal(detect['id'], id)

                # Strip the link and check it matches.
                stripped = self.a.strip_affiliate(url)
                self.assert_equal(stripped, stripped_test)

    @parameters(add_test_data)
    def test_add(self, data):
        if data is None:
            return

        name = data['name']
        url = data['url']

        # Set the proper affiliate ID in our config.
        self.config.update(data['config'])

        # Test adding affiliate link.
        added_url = self.a.add_affiliate(url)
        self.assert_equal(added_url, data['expected'])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAffiliateEngines))

    return suite

