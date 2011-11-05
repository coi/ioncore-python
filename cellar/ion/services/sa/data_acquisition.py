#!/usr/bin/env python

"""
@file ion/services/sa/data_acquisition.py
@author Michael Meisinger
@author Nalin Pilapitiya
@brief service for data acquisition
"""

'''
import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)
from twisted.internet import defer

import ion.util.procutils as pu
from ion.core.process.process import ProcessFactory
from ion.core.process.service_process import ServiceProcess, ServiceClient

from ion.services.sa.instrument_registry import InstrumentRegistryClient
from ion.services.sa.data_product_registry import DataProductRegistryClient

class DataAcquisitionService(ServiceProcess):
    """
    Data acquisition service interface.
    Data acquisition is the service coordinating the acquisition of samples
    packets and external block data for preparation into the ingestion service.
    """

    # Declaration of service
    declare = ServiceProcess.service_declare(name='data_acquisition',
                                          version='0.1.0',
                                          dependencies=[])


    def slc_init(self):
        self.irc = InstrumentRegistryClient()
        self.dprc = DataProductRegistryClient()

    @defer.inlineCallbacks
    def op_acquire_block(self, content, headers, msg):
        """
        Service operation: Acquire an entire, fully described version of a
        data set.
        """
        log.info('op_acquire_block: '+str(content))
        yield self.reply_ok(msg, {'value':'op_acquire_block_respond,'+str(content)}, {})


    @defer.inlineCallbacks
    def op_acquire_message(self, content, headers, msg):
        """
        Service operation: Acquire an increment of a data set.
        """
        log.info('op_acquire_message: '+str(content))
        yield self.reply_ok(msg, {'value':'op_acquire_message_respond, '+str(content)}, {})




class DataAcquisitionServiceClient(ServiceClient):
   """
   This is an exemplar service client that calls the Data acquisition service. It
   makes service calls RPC style.
   """
   def __init__(self, proc=None, **kwargs):
       if not 'targetname' in kwargs:
           kwargs['targetname'] = "data_acquisition"
       ServiceClient.__init__(self, proc, **kwargs)
   @defer.inlineCallbacks
   def acquire_block(self, text='Hi there'):
       yield self._check_init()
       (content, headers, msg) = yield self.rpc_send('acquire_block', text)
       log.info('Acquire block Service reply: '+str(content))
       defer.returnValue(str(content))

   @defer.inlineCallbacks
   def acquire_message(self, text='Hi there'):
       yield self._check_init()
       (content, headers, msg) = yield self.rpc_send('acquire_message', text)
       log.info('Acquire message Service reply: '+str(content))
       defer.returnValue(str(content))

# Spawn of the process using the module name
factory = ProcessFactory(DataAcquisitionService)
'''