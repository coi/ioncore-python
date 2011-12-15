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
AGENT_NAME='org_agent'
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
    
        

    @defer.inlineCallbacks
    def op_enroll(self, content, headers, msg):
        log.info('enrolling '+headers['user-id'] + ' in org '+headers['receiver-name'])
        self.store('enrolled',[headers['user-id'],headers['receiver-name']])
        yield self.reply_ok(msg, {'token':'IPC420'}, {})

    @defer.inlineCallbacks
    def op_contribute(self, content, headers, msg):
        log.info(headers['user-id']+' contributing '+str(content['resource_id'])+', action '+ str(content['action'])+ ' to org '+headers['receiver-name'])
        self.store('contributed',[headers['user-id'],content['resource_id'],content['action'],headers['receiver-name']])
        yield self.reply_ok(msg, 'success', {})

    @defer.inlineCallbacks
    def op_list_resources(self, content, headers, msg):
        org = headers['receiver-name']
        log.info('listing resources for ' + org)
        vars=self.governance_support.list(AGENT_NAME+'_facts','contributed','($user,$resource,$action,'+org+')')
        response=[]
        for var in vars:
            response.append([var['user'],var['resource'],var['action']])
        yield self.reply_ok(msg, response, {})

    @defer.inlineCallbacks
    def op_list_users(self, content, headers, msg):
        org=headers['receiver-name']
        log.info('listing users in ' + org)
        vars=self.governance_support.list(AGENT_NAME+'_facts','enrolled','($user,'+org+')')
        response=[]
        for var in vars:
            response.append(var['user'])
        yield self.reply_ok(msg, response, {})

    @defer.inlineCallbacks
    def op_validate_token(self, content, headers, msg):
        token=content['token']
        org=headers['receiver-name']
        log.info('validating token ' + token)
        vars=self.governance_support.list(AGENT_NAME+'_facts','token','($token,'+org+')')
        response=False
        for var in vars:
            if token==var['token']:
                response=True
                break
        yield self.reply_ok(msg, response, {})

    @defer.inlineCallbacks
    def op_validate_enrollment(self, content, headers, msg):
        user_id=headers['user-id']
        org=headers['receiver-name']
        log.info('validating user ' + user_id)
        vars=self.governance_support.list(AGENT_NAME+'_facts','enrolled','($user,'+org+')')
        response=False
        for var in vars:
            if user_id==var['user']:
                response=True
                break
        yield self.reply_ok(msg, response, {})

    def store(self,fact_name,arguments):
        self.governance_support.store(AGENT_NAME+'_facts',fact_name,arguments)

class OrgAgentServiceClient(ServiceClient):
    """
    This is an exemplar service client that calls the user_agent service. It
    makes service calls RPC style.
    """
    def __init__(self, proc=None, **kwargs):
        if not 'targetname' in kwargs:
            kwargs['targetname'] = AGENT_NAME
        ServiceClient.__init__(self, proc, **kwargs)
        

    @defer.inlineCallbacks
    def request(self, op, headers=None):
         yield self._check_init()
         log.info('here headers '+ str(headers) + ' op '+op)
         (content, headers, msg) = yield self.rpc_send(op,headers['content'],headers)
         defer.returnValue(str(content))

    
    def request_deferred(self, request=None):
        return self.rpc_send('service_request', request)

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
