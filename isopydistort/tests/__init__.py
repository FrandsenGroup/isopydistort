#!/usr/bin/env python
##############################################################################
#
# isopydistort        by Frandsen Group
#                     Benjamin A. Frandsen benfrandsen@byu.edu
#                     (c) 2023 Benjamin Allen Frandsen
#                      All rights reserved
#
# File coded by:    Benjamin Frandsen
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""Unit tests for isopydistort.
"""


# create logger instance for the tests subpackage
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
del logging


def testsuite():
    '''Build a unit tests suite for the isopydistort package.
    Return a unittest.TestSuite object.
    '''
    import unittest
    modulenames = '''
        isopydistort.tests.tests
    '''.split()
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    mobj = None
    for mname in modulenames:
        exec ('import %s as mobj' % mname)
        suite.addTests(loader.loadTestsFromModule(mobj))
    return suite


def test():
    '''Execute all unit tests for the isopydistort package.
    Return a unittest TestResult object.
    '''
    import unittest
    suite = testsuite()
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    return result


# End of file
