# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""
First we need to grok our test to register the resources:
>>> grok('silva.resourceinclude.tests.resource')

Head requests
=============

Now, we should be able to do request on our resources, here a CSS file:
>>> resource_path = '/++resource++silva.resourceinclude.tests.resource'
>>> response = http('HEAD %s/style.css HTTP/1.1' % resource_path)
>>> response.header_output.status
200
>>> headers = response.header_output.headers
>>> headers.keys()
['Last-Modified', 'Content-Length', 'Expires',
 'Content-Type', 'Cache-Control']
>>> headers['Content-Type']
'text/css'
>>> headers['Content-Length']
'0'
>>> headers['Cache-Control']
'public,max-age=31536000'

Image
-----

On an image for instance:
>>> response = http('HEAD %s/images/img01.gif HTTP/1.1' % resource_path)
>>> response.header_output.status
200
>>> headers = response.header_output.headers
>>> headers.keys()
['Last-Modified', 'Content-Length', 'Expires',
 'Content-Type', 'Cache-Control']
>>> headers['Content-Type']
'image/gif'
>>> headers['Content-Length']
'0'
>>> headers['Cache-Control']
'public,max-age=31536000'

Container
---------

On a resource directory:
>>> response = http('HEAD %s/images HTTP/1.1' % resource_path)
>>> response.header_output.status
200
>>> headers = response.header_output.headers
>>> headers.keys()
['Last-Modified', 'Content-Length', 'Expires',
 'Content-Type', 'Cache-Control']
>>> headers['Content-Type']
'text/plain'
>>> headers['Content-Length']
'0'
>>> headers['Cache-Control']
'public,max-age=31536000'


"""
