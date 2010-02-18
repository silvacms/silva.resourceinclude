# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '1.1dev'

setup(name='silva.resourceinclude',
      version=version,
      description="z3c.resourceinclude support for Silva",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
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
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'chameleon.zpt',
          'five.grok',
          'martian',
          'plone.memoize',
          'setuptools',
          'silva.core.conf',
          'silva.core.views',
          'slimmer',
          'zope.component',
          'zope.configuration',
          'zope.datetime',
          'zope.interface',
          'zope.publisher',
          'zope.schema',
          ],
      )
