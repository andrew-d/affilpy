from __future__ import with_statement, print_function

from .helpers import *

import os
import unittest

ensure_in_path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import affilpy


def suite():
    # Import test suites here.
    from .test_main import suite as suite_1

    suite = unittest.TestSuite()
    suite.addTest(suite_1())

    return suite


def main():
    """
    This runs the our tests, suitable for a command-line application
    """
    unittest.main(defaultTest='suite', exit=False)
    print("Number of assertions: {0}".format(BaseTestCase.number_of_assertions))
    print("")

if __name__ == "__main__":
    main()

