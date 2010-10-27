# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '2.2.1dev'

tests_require = [
    'infrae.wsgi [test]',
    ]

setup(name='silva.resourceinclude',
      version=version,
      description="z3c.resourceinclude like support for Silva",
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
      author_email='info@infrae.com',
      url='http://svn.infrae.com/silva.resourceinclude/trunk',
      license='ZPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Chameleon',
          'five.grok',
          'martian',
          'setuptools',
          'silva.core.cache',
          'silva.core.conf',
          'silva.core.views',
          'cssmin',
          'zope.component',
          'zope.configuration',
          'zope.datetime',
          'zope.interface',
          'zope.publisher',
          'zope.schema',
          'zope.traversing',
          ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
