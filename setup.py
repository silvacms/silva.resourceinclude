# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '2.2.2dev'

tests_require = [
    'infrae.wsgi [test]',
    'infrae.testbrowser',
    'zope.event',
    ]

setup(name='silva.resourceinclude',
      version=version,
      description="z3c.resourceinclude like support for Silva 2",
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
      url='https://github.com/silvacms/silva.resourceinclude',
      license='ZPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Chameleon',
          'cssmin',
          'five.grok',
          'martian',
          'setuptools',
          'silva.core.cache',
          'silva.core.conf',
          'silva.core.views',
          'zope.component',
          'zope.configuration',
          'zope.datetime',
          'zope.interface',
          'zope.processlifetime',
          'zope.publisher',
          'zope.schema',
          'zope.testing',
          'zope.traversing',
          ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
