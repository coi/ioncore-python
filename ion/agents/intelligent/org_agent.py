#!/usr/bin/env python

"""
@file ion/play/org_agent_service.py
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
from ion.agents.intelligent.kb import policy_support

from ion.core.intercept.governance_support import GovernanceSupportServiceClient

REQUEST='request'

class OrgAgentService(ServiceProcess):
    """
    Example service interface
    """
    # Declaration of service
    declare = ServiceProcess.service_declare(name='orgagent',
                                             version='0.1.0',
                                             dependencies=[])

    def __init__(self, *args, **kwargs):
        # Service class initializer. Basic config, but no yields allowed.
        ServiceProcess.__init__(self, *args, **kwargs)
        log.info('OrgAgentService.__init__()')

    def slc_init(self):
        # Service life cycle state. Initialize service here. Can use yields.
        pass
    
    def hi(self, name):
        print "hi " + name
        

    @defer.inlineCallbacks
    def op_enroll(self, request_content, headers, msg):
        log.info('enroll request content: '+str(request_content))

        gsc = GovernanceSupportServiceClient(proc=self)
        #pass the message to the gsc for governance interpretation
        response=gsc.check(invocation.content)
        print response

        #policy_response = policy_support.check(headers)
        #if policy_response!='denied':
        #    rasc = ResourceAgentServiceClient()
        #    request_content['role']=policy_response['role']
        #    log.info('request to resource agent '+str(request_content))
        #    policy_response = yield rasc.execute_request(request_content)
        yield self.reply_ok(msg, response, {})

    @defer.inlineCallbacks
    def op_list_resources(self, request_content, headers, msg):
        log.info('listing resources')

class OrgAgentServiceClient(ServiceClient):
    """
    This is an exemplar service client that calls the user_agent service. It
    makes service calls RPC style.
    """
    def __init__(self, proc=None, **kwargs):
        if not 'targetname' in kwargs:
            kwargs['targetname'] = "orgagent"
        ServiceClient.__init__(self, proc, **kwargs)
        

    @defer.inlineCallbacks
    def request(self, request_content=None):
        yield self._check_init()
        log.info('Org recieved: '+str(request_content))
        (request_content, headers, msg) = yield self.rpc_send(request_content[REQUEST],request_content)
        log.info('Org reply: '+str(request_content))
        defer.returnValue(str(request_content))

    
    def request_deferred(self, request=None):
        return self.rpc_send('service_request', request)

    def hi(self, name):
        print "hi " + name
# Spawn of the process using the module name
factory = ProcessFactory(OrgAgentService)



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
