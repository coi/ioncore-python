#!/usr/bin/env python

"""
@file ion/play/user_agent_service.py
@author Prashant Kediyal
@brief An example service definition that can be used as template.
"""

print str(__name__)
import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)


from twisted.internet import defer

from ion.core.process.process import ProcessFactory
from ion.core.process.service_process import ServiceProcess, ServiceClient
from ion.agents.intelligent.resource_agent import ResourceAgentServiceClient
from ion.agents.intelligent.org_agent import OrgAgentServiceClient

AGENT_NAME='user_agent'

class UserAgentService(ServiceProcess):
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
        log.info('UserAgentService.__init__()')

    def slc_init(self):
        # Service life cycle state. Initialize service here. Can use yields.
        pass
    
    @defer.inlineCallbacks
    def op_resource_request(self, content, headers, msg):
        op=content['action']
        headers={'receiver-name':content['resource_id'], 'op':op, 'content':content['content'], 'user-id':headers['user-id']}

        rasc = ResourceAgentServiceClient()
        response = yield rasc.request(op,headers)
        if response is None:
            response = 'failure'
            log.info('No response received from the resource agent')
        yield self.reply_ok(msg, response, {})

    @defer.inlineCallbacks
    def op_org_request(self, content, headers, msg):
        op=content['action']
        headers={'receiver-name':content['resource_id'], 'op':op, 'content':content['content'], 'user-id':headers['user-id']}

        oasc = OrgAgentServiceClient()
        response = yield oasc.request(op,headers)
        if response is None:
            response = 'failure'
            log.info('No response received from the org agent')
        yield self.reply_ok(msg, response, {})


class UserAgentServiceClient(ServiceClient):
    """
    This service client calls the user_agent service. It
    makes service calls RPC style.
    """
    def __init__(self, proc=None, **kwargs):
        if not 'targetname' in kwargs:
            kwargs['targetname'] = AGENT_NAME
        ServiceClient.__init__(self, proc, **kwargs)
        

    @defer.inlineCallbacks
    def request(self, op, headers=None):
        yield self._check_init()
        (content, headers, msg) = yield self.rpc_send(op,headers['content'],headers)
        defer.returnValue(str(content))
        
    
    def request_deferred(self, request=None):
        return self.rpc_send('service_request', request)

# Spawn of the process using the module name
factory = ProcessFactory(UserAgentService)



"""
from ion.play import user_agent_service as h
spawn(h)

# TODO:
# supervisor process is #1, our user_agent_service should be #2.
# sending to 1 results in a callback with no data, sending to 2 does not
# ever call back.
send(1, {'op':'hello','content':'Hello you there!'})

from ion.play.user_agent_service import UserAgentServiceClient
hc = UserAgentServiceClient()
hc.hello()
"""
