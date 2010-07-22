"""
@file ion/services/coi/objstore.py
@author Dorian Raymer
"""

import logging
logging = logging.getLogger(__name__)

from zope import interface

from twisted.internet import defer

from ion.services import base_service 
from ion.core import base_process
from ion.data import store
from ion.data.datastore import cas
from ion.data.datastore import objstore

class Serializer(object):

    def encode(self, obj, encoder=None):
        """
        @brief Operates on sendable objects
        """
        return obj.encode()

    def decode(self, bytes, decoder=None):
        """
        @brief Operates on encoded sendable objects
        """
        return  

class ObjectStoreService(base_service.BaseService):
    """
    The service end of Distributed ObjectStore that mediates between the message based
    interface and the actual implementation.

    """

    declare = base_service.BaseService.service_declare(name='objstore', version='0.1.0', dependencies=[]) 

    @defer.inlineCallbacks
    def slc_init(self):
        """
        setup creation of ObjectStore instance 
        decide on which backend to use based on option

        It would be nice to separate the existence/creation of the
        ObjectStores IStore backend from the instantiation of ObjectStore.
        That way, if IStore is an in memory dict, it can be used by
        different IObjectStores; if IStore is a Redis client, it's
        connection can be managed elsewhere....actually, that is a good
        question, how is that connection managed?
        """
        backend = yield store.Store.create_store()
        self.objstore = yield objstore.ObjectStore(backend)


    def op_clone(self, content, headers, msg):
        """
        """

    def op_create(self, content, headers, msg):
        """
        """

    @defer.inlineCallbacks
    def op_get(self, content, headers, msg):
        """
        @brief The content should be a 'cas content' id
        @note The backend decodes right before we re-encode. Is this
        necessary? 
        Ans: cas.BaseObject has a cache for this encoding step
        """
        id = content
        try:
            obj = yield self.objstore.get(id)
            #data = serializer.encode(obj)
            data = obj.encode()
            yield self.reply_ok(msg, data)
        except cas.CAStoreError, e:
            yield self.reply_err(msg, None)

    @defer.inlineCallbacks
    def op_put(self, content, headers, msg):
        """
        """
        id = content['id']
        data = content['data']
        try:
            obj = self.objstore.decode(data)
            id_local = yield self.objstore.put(obj)
            if not id == id_local:
                yield self.reply_err(msg, 'Content inconsistency')
            yield self.reply_ok(msg, id) 
        except cas.CAStoreError, e:
            yield self.reply_err(msg, e)




class ObjectStoreClient(base_service.BaseServiceClient, cas.CAStore):
    """
    The client end of Distributed ObjectStore that presents the same
    interface as the actual ObjectStore.

    The main variable is the name and sys-name of the service. All else
    should be invariant.

    This is where a caching/mirroring-backend layer can exist.
    """

    interface.implements(objstore.IObjectStore, cas.ICAStore)

    objectChassis = objstore.ObjectChassis

    def create(self, name, baseClass):
        """
        @brief Create a new DataObject with the structure of baseClass.
        @param name Unique identifier of data object.
        @param baseClass DataObject class.
        @retval defer.Deferred that succeeds with an instance of
        objectChassis.
        @todo Change name to id
        """

    @defer.inlineCallbacks
    def clone(self, name):
        """
        @brief Pull data object out of distributed store into local store.
        @param name Unique identifier of data object.
        @retval defer.Deferred that succeeds with an instance of
        objectChassis.
        @todo Change name to id.
        """
        (content, headers, msg) = yield self.rpc_send('clone', name)
        if content['status'] == 'OK':
            obj = content['value']
            defer.returnValue(obj)
        else:
            defer.returnValue(None) #what to return?

        
        

    def get(self, id):
        """
        @brief get content object.
        @param id of content object.
        @retval defer.Deferred that fires with an object that provides
        cas.ICAStoreObject.
        """
        d = self.rpc_send('get', id)
        d.addCallback(self._get_callback, id)
        d.addErrback(self._get_errback)
        return d

    def _get_callback(self, (content, headers, msg), id):
        """
        """
        data = content['value'] # This should not be content['value']
        if content['status'] == 'OK':
            """@todo make 'ok' a bool instead
            """
            obj = self.decode(data)
            if not id == cas.sha1(obj, bin=False):
                raise cas.CAStoreError("Object Integrity Error!")
            return obj
        else:
            """@todo should check for not found in store error
            """
            raise cas.CAStoreError("Client Error")

    def _get_errback(self, reason):
        return reason

    def put(self, obj):
        """
        @brief Write a content object to the store.
        @param obj instance providing cas.ICAStoreObject.
        @retval defer.Deferred that fires with the obj id.
        """
        data = obj.encode()
        id = cas.sha1(data, bin=False)
        d = self.rpc_send('put', {'id':id, 'data':data})
        d.addCallback(self._put_callback)
        #d.addErrback
        return d


    def _put_callback(self, (content, headers, msg)):
        """
        """
        id = content['value']
        return id

factory = base_process.ProtocolFactory(ObjectStoreService)


