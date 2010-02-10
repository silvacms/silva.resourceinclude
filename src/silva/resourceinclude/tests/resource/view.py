# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""
>>> from silva.resourceinclude.tests.resource import static_dir
>>> from silva.resourceinclude.interfaces import IResource

Viewing Resource
================

So we can create a directory resource:
>>> from silva.resourceinclude.resource import DirectoryResource
>>> resources = DirectoryResource(
...      'silva.resourceinclude.tests.resource', static_dir)

We can get a factory out of it:
>>> from silva.resourceinclude.resource import ResourceFactory
>>> resources_factory = ResourceFactory(resources)

And if you have a request, you can download / have information on
your resource:
>>> from zope.publisher.browser import TestRequest
>>> request = TestRequest()
>>> resources_view = resources_factory(request)
>>> resources_view
<silva.resourceinclude.resource.ResourceView object at ...>

From here you can traverse to sub resources:
>>> resource_css_view = resources_view.publishTraverse(request, 'style.css')
>>> resource_css_view
<silva.resourceinclude.resource.ResourceView object at ...>
>>> resource_images_view = resources_view.publishTraverse(request, 'images')
>>> resource_image_view = resource_images_view.publishTraverse(request, 'img01.gif')
>>> resources_view.publishTraverse(request, 'unknown')
Traceback (most recent call last):
  ...
NotFound: Object: <silva.resourceinclude.resource.ResourceView object at ...>, name: 'unknown'

Getting the relative path of a resource
---------------------------------------

You can get the relative path to root of the resource directory:
>>> resources_view.get_relative_path()
['silva.resourceinclude.tests.resource']
>>> resource_css_view.get_relative_path()
['silva.resourceinclude.tests.resource', 'style.css']
>>> resource_image_view.get_relative_path()
['silva.resourceinclude.tests.resource', 'images', 'img01.gif']

Getting the URL of a resource
-----------------------------

And so you can the URL of the resource:
>>> resources_view()
u'http://localhost/root/++resource++silva.resourceinclude.tests.resource'
>>> resource_css_view()
u'http://localhost/root/++resource++silva.resourceinclude.tests.resource/style.css'
>>> resource_image_view()
u'http://localhost/root/++resource++silva.resourceinclude.tests.resource/images/img01.gif'

"""
