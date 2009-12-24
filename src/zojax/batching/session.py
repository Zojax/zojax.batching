##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from zope import interface
from zope.traversing.api import getPath
from zope.session.interfaces import ISession
from z3c.batching.batch import Batch

from batch import Batches
from interfaces import IBatch

SESSIONKEY = 'zojax.batching'


class SessionBatch(Batch):
    interface.implements(IBatch)

    def __init__(self, sequence, start=0, size=20,
                 batches=None, context=None, request=None,
                 prefix='', queryparams={}):
        self.context = context
        self.request = request
        self.prefix = prefix

        if request is not None:
            rkey = self.prefix + 'bstart'

            if context is None:
                key = rkey
            else:
                key = '%s:%s'%(getPath(context), rkey)

            if rkey in request:
                try:
                    rstart = int(request.get(rkey, start))

                    data = ISession(request)[SESSIONKEY]
                    data[key] = rstart

                    start = rstart
                except:
                    pass
            else:
                data = ISession(request)[SESSIONKEY]
                start = data.get(key, start)

        if start >= len(sequence):
            start = 0

        super(SessionBatch, self).__init__(sequence, start, size, batches)

        if batches is None:
            self.batches = Batches(self)

        self.queryparams = queryparams
