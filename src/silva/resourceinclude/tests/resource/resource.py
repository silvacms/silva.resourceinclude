"""

   >>> from silva.resourceinclude.tests.resource import static_dir
   >>> from silva.resourceinclude.interfaces import IResource

   So we can create a directory resource:
   >>> from silva.resourceinclude.resource import DirectoryResource
   >>> resources = DirectoryResource(
   ...      'silva.resourceinclude.tests.resource.static', static_dir)

   >>> resources
   <silva.resourceinclude.resource.DirectoryResource object at ...>
   >>> verifyObject(IResource, resources)
   True

   A directory as no data but you can access existing sub resources:
   >>> resources.data()
   u''
   >>> resources.content_type
   >>> resources['style.css']
   <silva.resourceinclude.resource.FileResource object at ...>
   >>> resources['images']
   <silva.resourceinclude.resource.DirectoryResource object at ...>
   >>> resources['images']['img01.gif']
   <silva.resourceinclude.resource.FileResource object at ...>
   >>> resources['unknown']
   Traceback (most recent call last):
     ...
   KeyError: 'unknown'

   A file as some data, but no sub resources:
   >>> file_resource = resources['style.css']

   >>> verifyObject(IResource, file_resource)
   True
   >>> print file_resource.data()
   body {
       margin: auto;
   }
   >>> file_resource.content_type
   'text/css'
   >>> file_resource['something']
   Traceback (most recent call last):
     ...
   KeyError: 'something'

   The content type is computed from the extension of the file:
   >>> image_resource = resources['images']['img01.gif']

   >>> image_resource.content_type
   'image/gif'

"""

