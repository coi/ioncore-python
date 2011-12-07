#!/usr/bin/env python

"""
@file ion/agent/intelligent/ressource_agent.py
@author Prashant Kediyal
@brief An example service definition that can be used as template.
"""

import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)
from twisted.internet import defer

from ion.core.process.process import ProcessFactory
from ion.core.process.service_process import ServiceProcess, ServiceClient
from ion.agents.intelligent.kb import policy_support

REQUEST='request'
class ResourceAgentService(ServiceProcess):
    """
    Example service interface
    """
    # Declaration of service
    declare = ServiceProcess.service_declare(name='resourceagent',
                                             version='0.1.0',
                                             dependencies=[])

    def __init__(self, *args, **kwargs):
        # Service class initializer. Basic config, but no yields allowed.
        ServiceProcess.__init__(self, *args, **kwargs)
        log.info('ResourceAgentService.__init__()')

    def slc_init(self):
        # Service life cycle state. Initialize service here. Can use yields.
        pass

    @defer.inlineCallbacks
    def op_service_request(self, request_content, headers, msg):
        log.info('op_execute_request: '+str(request_content))       
        #permit_decision = policy_support.check(headers)
        #yield self.reply_ok(msg, permit_decision, {})
        yield self.reply_ok(msg, 'success', {})

class ResourceAgentServiceClient(ServiceClient):
    """
    This is an exemplar service client that calls the resource agent service. It
    makes service calls RPC style.
    """
    def __init__(self, proc=None, **kwargs):
        #print proc + 'helloSC kwargs are' + kwargs
        if not 'targetname' in kwargs:
            kwargs['targetname'] = "resourceagent"
        ServiceClient.__init__(self, proc, **kwargs)

    @defer.inlineCallbacks
    def request(self, request_content=None):
        yield self._check_init() 
        (request_content, headers, msg) = yield self.rpc_send(request_content[REQUEST],request_content)
        log.info('Service reply: '+str(request_content))
        defer.returnValue(str(request_content))
        
    
    def request_deferred(self, text='Hi there requester'):
        return self.rpc_send('execute_request', text)

# Spawn of the process using the module name
factory = ProcessFactory(ResourceAgentService)



"""
from ion.play import resource_agent as r
spawn(r)

# TODO:
# supervisor process is #1, our resource_agent should be #2.
# sending to 1 results in a callback with no data, sending to 2 does not
# ever call back.
send(1, {'op':'helloresource','content':'Hello you there resource!'})

from ion.play.hello_service import HelloServiceClient
hc = ResourceAgentServiceClient()
hc.hello()
"""
