# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
import doctest

from infrae.wsgi.testing import BrowserLayer, suite_from_package, http, Browser
from zope.interface.verify import verifyObject
import silva.resourceinclude


layer = BrowserLayer(silva.resourceinclude, zcml_file='configure.zcml')
globs = {'verifyObject': verifyObject,
         'getRootFolder': layer.get_application,
         'http': http,
         'Browser': Browser,
         'grok': layer.grok,}


def create_test(build_test_suite, name):
    test =  build_test_suite(
        name,
        globs=globs,
        optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)
    test.layer = layer
    return test


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(suite_from_package(
            'silva.resourceinclude.tests.collector', create_test))
    suite.addTest(suite_from_package(
            'silva.resourceinclude.tests.directive', create_test))
    suite.addTest(suite_from_package(
            'silva.resourceinclude.tests.resource', create_test))
    return suite

