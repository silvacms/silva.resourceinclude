# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from pkg_resources import resource_listdir

from zope.interface.verify import verifyObject
from zope.testing import doctest

from Testing import ZopeTestCase

import five.grok.testing

from Products.Silva.tests.SilvaBrowser import SilvaBrowser
from Testing.ZopeTestCase.zopedoctest.functional import getRootFolder, sync
from silva.resourceinclude.testing import ResourceIncludeLayer

extraglobs = {'SilvaBrowser': SilvaBrowser,
              'verifyObject': verifyObject,
              'getRootFolder': getRootFolder,
              'sync': sync,
              'grok': five.grok.testing.grok,}

def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'silva.resourceinclude.tests.%s.%s' % (name, filename[:-3])
        test = ZopeTestCase.FunctionalDocTestSuite(
            dottedname,
            extraglobs=extraglobs,
            optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)

        test.layer = ResourceIncludeLayer
        suite.addTest(test)
    return suite

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(suiteFromPackage('resources'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
