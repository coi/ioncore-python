"""
@file ion/services/coi/test/test_objstore.py
@author Dorian Raymer
"""

import logging

from twisted.internet import defer
from twisted.trial import unittest

from ion.test import iontest

from ion.services.coi import objstore
from ion.data.datastore import cas
from ion.data.datastore.test import test_cas


logging = logging.getLogger(__name__)

class ObjectStoreServiceTest(iontest.IonTestCase):

    @defer.inlineCallbacks
    def setUp(self):
        yield self._start_container()
        services = [
                {'name':'objstore',
                    'module':'ion.services.coi.objstore',
                    'class':'ObjectStoreService',
                    }
                ]
        sup = yield self._spawn_processes(services)
        self.object_store = objstore.ObjectStoreClient(targetname='objstore')
        self.object_store.attach()

    @defer.inlineCallbacks
    def tearDown(self):
        yield self._stop_container()

    @defer.inlineCallbacks
    def test_put(self):
        b = cas.Blob('test')
        id = yield self.object_store.put(b)
        self.failUnlessEqual(id, cas.sha1(b, bin=False))

    @defer.inlineCallbacks
    def test_get(self):
        b = cas.Blob('test')
        id = yield self.object_store.put(b)

        b_out = yield self.object_store.get(id)
        self.failUnlessEqual(b.encode(), b_out.encode())
        

class ObjectStoreServiceCASTest(iontest.IonTestCase, test_cas.CAStoreTest):

    @defer.inlineCallbacks
    def setUp(self):
        yield self._start_container()
        services = [
                {'name':'objstore',
                    'module':'ion.services.coi.objstore',
                    'class':'ObjectStoreService',
                    }
                ]
        sup = yield self._spawn_processes(services)
        self.cas = objstore.ObjectStoreClient(targetname='objstore')
        self.cas.attach()

    @defer.inlineCallbacks
    def tearDown(self):
        yield self._stop_container()


