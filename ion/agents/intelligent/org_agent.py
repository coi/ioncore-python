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
from ion.core.intercept.governance_support import GovernanceSupport

OP='op'
DROP='drop'
ENROLL='enroll'
AGENT_NAME='orgagent'
class OrgAgentService(ServiceProcess):
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
        log.info('OrgAgentService.__init__()')

    def slc_init(self):
        # Service life cycle state. Initialize service here. Can use yields.
        self.governance_support = GovernanceSupport()
        pass
    
    def hi(self, name):
        print "hi " + name
        

    @defer.inlineCallbacks
    def op_enroll(self, request_content, headers, msg):
        log.info('enrolling '+request_content['user_id'] + ' in org '+request_content['resource_id'])
        self.store('enrolled',[request_content['resource_id']+','+request_content['user_id']])
        yield self.reply_ok(msg, 'success', {})

    @defer.inlineCallbacks
    def op_contribute(self, request_content, headers, msg):
        log.info('contributing '+str(request_content[resource_id]['RESOURCE']) + ' to org '+request_content[resource_id]['ORG'])
        self.store('contributed',[request_content[user_id]+','+request_content[resource_id]['RESOURCE']+','+request_content[resource_id]['ORG']])
        yield self.reply_ok(msg, 'success', {})

    #@defer.inlineCallbacks
    def op_list_resources(self,org):
        log.info('listing resources')
        vars=self.governance_support.list(AGENT_NAME+'_facts','contributed','($user,$resource,'+org+')')
        response=[]
        for var in vars:
            response.append([var['user'],var['resource']])
        return response
        #yield self.reply_ok(msg, resources, {})

    #@defer.inlineCallbacks
    def op_list_users(self,org):
        log.info('listing users')
        vars=self.governance_support.list(AGENT_NAME+'_facts','enrolled','('+org+',$user)')
        response=[]
        for var in vars:
            response.append(var['user'])
        return response

        #yield self.reply_ok(msg, 'success', {})
            

    def store(self,fact_name,arguments):
        self.governance_support.store(AGENT_NAME+'_facts',fact_name,arguments)

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
        (request_content, headers, msg) = yield self.rpc_send(request_content[OP],request_content)
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
