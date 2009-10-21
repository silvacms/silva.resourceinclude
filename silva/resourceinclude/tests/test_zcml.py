# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from Testing import ZopeTestCase

from silva.resourceinclude.testing import ResourceIncludeLayer

class ResourceIncludeTest(ZopeTestCase.FunctionalTestCase):

    layer = ResourceIncludeLayer

    def test_me(self):
        pass



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ResourceIncludeTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
