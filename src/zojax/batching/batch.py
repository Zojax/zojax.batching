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
import cgi, urlparse, urllib

from zope import interface, component
from zope.app.pagetemplate import ViewPageTemplateFile

from z3c.batching.batch import Batch as BaseBatch
from z3c.batching.batch import Batches as BaseBatches
from zojax.layout.interfaces import IPageletContext

from interfaces import IBatch, IBatchView


class Batch(BaseBatch):
    interface.implements(IBatch)

    def __init__(self, sequence, start=0, size=20,
                 batches=None, context=object(), request=None, 
                 prefix='', queryparams={}):
        self.context = context
        self.request = request
        self.prefix = prefix

        if request is not None:
            try:
                rstart = int(request.get(self.prefix+'bstart', start))
            except:
                rstart = start
            start = rstart

        if start >= len(sequence):
            start = 0

        super(Batch, self).__init__(sequence, start, size, batches)
        if batches is None:
            self.batches = Batches(self)

        self.queryparams = {}


class Batches(BaseBatches):

    def __init__(self, batch):
        self.batch = batch
        super(Batches, self).__init__(batch)

    def __getitem__(self, key):
        if key not in self._batches:
            if key < 0:
                key = self.total + key

            batch = Batch(
                self.sequence, key*self.size,
                self.size, self, prefix=self.batch.prefix)
            self._batches[batch.index] = batch

        try:
            return self._batches[key]
        except KeyError:
            raise IndexError(key)


@component.adapter(IBatch)
@interface.implementer(IPageletContext)
def getBatchContext(batch):
    return batch.context


class BatchView(object):
    interface.implements(IBatchView)

    template = ViewPageTemplateFile('batch.pt')

    def render(self, batch_url=None):
        context = self.context
        if not bool(context.previous or context.next):
            return u''

        if batch_url:
            self.batch_url = batch_url
        else:
            self.batch_url = self.request.URL

        return super(BatchView, self).render()

    def getUrl(self, start):
        startKey = self.context.prefix+'bstart'
        reqs = self.request.getURL()
        parsed_query = list(urlparse.urlparse(reqs))
        params = cgi.parse_qsl(self.request.get('QUERY_STRING','')) # not good
        for key, value in list(params):
            if key == startKey:
                params.remove((key, value))

        params.extend(self.context.queryparams.items())
        params.append((startKey, start))
        parsed_query[-2] = urllib.urlencode(params)
        return urlparse.urlunparse(parsed_query)

    def getNextUrl(self):
        return self.getUrl(self.context.next.start)

    def getPreviousUrl(self):
        return self.getUrl(self.context.previous.start)
