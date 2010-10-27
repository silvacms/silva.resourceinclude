# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os
import operator


def filter_resources(resources, content_type):
    """Filter a list of resources out of list_production_resources.
    """
    return sorted(filter(lambda r: r[3] == content_type, resources))


def display_resources((layer, context, managers, type),):
    """Display list_production_resources resources.
    """
    resources = ', '.join(map(lambda p: os.path.basename(p),
                                reduce(operator.add,
                                       map(operator.attrgetter('names'),
                                           managers))))
    print "%s: (%s, %s) <%s>" % (type, layer.__name__, context.__name__, resources)
