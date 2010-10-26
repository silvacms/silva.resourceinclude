# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


def list_base_layers(layer):
    """List all layers used by the given layer.
    """
    yield layer
    for base in layer.__bases__:
        if base in (
            IDefaultBrowserLayer, IBrowserSkinType, IBrowserRequest, Interface):
            continue
        for base_base in list_base_layers(base):
            yield base_base


def list_base_interfaces(interface):
    """List all interfaces regrouped by this one.
    """
    yield interface
    for base in interface.__bases__:
        for base_base in list_base_interfaces(base):
            yield base_base
