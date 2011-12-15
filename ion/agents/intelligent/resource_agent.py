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

AGENT_NAME='resource_agent'
class ResourceAgentService(ServiceProcess):
    """
    Example service interface
    """
    # Declaration of service
    declare = ServiceProcess.service_declare(name=AGENT_NAME,
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
    def op_get_temp(self, content, headers, msg):
        yield self.reply_ok(msg, 'temperature on '+headers['receiver-name']+ ' is 13 degrees fahrenheit', {})

class ResourceAgentServiceClient(ServiceClient):
    """
    This is an exemplar service client that calls the resource agent service. It
    makes service calls RPC style.
    """
    def __init__(self, proc=None, **kwargs):
        #print proc + 'helloSC kwargs are' + kwargs
        if not 'targetname' in kwargs:
            kwargs['targetname'] = AGENT_NAME
        ServiceClient.__init__(self, proc, **kwargs)

    @defer.inlineCallbacks
    def request(self, op, headers=None):
        yield self._check_init()
        (content, headers, msg) = yield self.rpc_send(op,headers['content'],headers)
        defer.returnValue(str(content))
    
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
