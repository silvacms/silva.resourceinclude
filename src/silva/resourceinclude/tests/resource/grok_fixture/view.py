
from OFS.Folder import Folder
from five import grok


class AdvancedFolder(grok.View):
    """Advanced View for a folder.
    """
    grok.context(Folder)

