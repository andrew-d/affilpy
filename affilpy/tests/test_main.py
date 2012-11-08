from __future__ import print_function

from .helpers import BaseTestCase
import unittest


class TestMain(BaseTestCase):
    pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMain))

    return suite

