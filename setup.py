# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '1.0dev'

setup(name='silva.resourceinclude',
      version=version,
      description="z3c.resourceinclude support for Silva",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Zope Public License",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Zope2",
          ],
      keywords='zope2 resourceinclude z3c',
      author='Sylvain Viollon',
      author_email='zope-dev@zope.org',
      url='http://svn.infrae.com/silva.resourceinclude/trunk',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['silva'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'martian',
          'silva.core.views',
          'silva.core.conf',
          'zope.app.publisher',
          'zope.app.cache',
          'zope.contentprovider',
          'chameleon.zpt',
          'plone.memoize',
          ],
      )
