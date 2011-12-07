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

from ion.agents.intelligent.kb import policy_support
REQUEST='request'
class UserAgentService(ServiceProcess):
    """
    Example service interface
    """
    # Declaration of service
    declare = ServiceProcess.service_declare(name='useragent',
                                             version='0.1.0',
                                             dependencies=[])
    token=''

    def __init__(self, *args, **kwargs):
        # Service class initializer. Basic config, but no yields allowed.
        ServiceProcess.__init__(self, *args, **kwargs)
        log.info('UserAgentService.__init__()')

    def slc_init(self):
        # Service life cycle state. Initialize service here. Can use yields.
        pass
    
    def hi(self, name):
        print "hi " + name
        
    @defer.inlineCallbacks
    def op_service_request(self, request_content, headers, msg):
        log.info('op_service_request content: '+str(request_content))
        log.info('op_service_request msg: '+str(msg))
        log.info('op_service_request header: '+str(headers))
        rasc = ResourceAgentServiceClient()
        log.info('request to resource agent '+str(request_content))
        response = yield rasc.request(request_content)
        if response is None:
            response = 'failure'
            log.info('No response received from the resource agent')
        yield self.reply_ok(msg, response, {})

    @defer.inlineCallbacks
    def op_enroll(self, request_content, headers, msg):
        log.info('op_enroll content: '+str(request_content))
        log.info('op_enroll msg: '+str(msg))
        log.info('op_enroll header: '+str(headers))
        oasc = OrgAgentServiceClient()
        log.info('request to org agent '+str(request_content))
        response = yield oasc.request(request_content)
        if response is None:
            response = 'failure'
            log.info('No response received from the org agent')
        yield self.reply_ok(msg, response, {})

class UserAgentServiceClient(ServiceClient):
    """
    This is an exemplar service client that calls the user_agent service. It
    makes service calls RPC style.
    """
    def __init__(self, proc=None, **kwargs):
        if not 'targetname' in kwargs:
            kwargs['targetname'] = "useragent"
        ServiceClient.__init__(self, proc, **kwargs)
        

    @defer.inlineCallbacks
    def request(self, request_content=None):
        yield self._check_init()
        log.info('requested ' + request_content[REQUEST])
        (request_content, headers, msg) = yield self.rpc_send(request_content[REQUEST],request_content)
        log.info('Service reply: '+str(request_content))
        defer.returnValue(str(request_content))
        
    
    def request_deferred(self, request=None):
        return self.rpc_send('service_request', request)

    def hi(self, name):
        print "hi " + name
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
