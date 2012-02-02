#!/usr/bin/env python

"""
@file ion/play/org_agent_service.py
@author Prashant Kediyal
@brief An example service definition that can be used as template.
"""

import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)

from twisted.internet import defer
from ion.core.process.process import ProcessFactory
from ion.core.process.service_process import ServiceProcess
from ion.core.agents.agent_service_process import AgentServiceProcess, AgentServiceClient

AGENT_NAME='org_agent'

class OrgAgentService(AgentServiceProcess):
    """
    Example service interface
    """
    # Declaration of service
    declare = ServiceProcess.service_declare(name=AGENT_NAME,
                                             version='0.1.0',
                                             dependencies=[])

    def __init__(self, *args, **kwargs):
        self.AGENT_NAME=AGENT_NAME
        AgentServiceProcess.__init__(self, *args, **kwargs)
        log.info('OrgAgentService.__init__()')

    @defer.inlineCallbacks
    def enroll(self, content, headers, msg):
        log.info('enrolling '+headers['user-id'] + ' in org '+headers['receiver-name'])
        parameters=(headers['user-id'], content['role'], headers['receiver-name'])
        response=('enrolled',parameters)
        yield self.reply_ok(msg, response, {})

    @defer.inlineCallbacks
    def sanction(self, content, headers, msg):
        op,op_id,sanctioned_user=content
        consequent=[sanctioned_user, headers['receiver-name']]
        response=('ejected',consequent)
        yield self.reply_ok(msg, response, {})

    @defer.inlineCallbacks
    def contribute(self, content, headers, msg):
        log.info(headers['user-id']+' contributing '+str(content['resource_id'])+', action '+ str(content['action'])+ ' to org '+headers['receiver-name'])
        consequent=[headers['user-id'],content['resource_id'],content['action'],headers['receiver-name']]
        response=('contributed',consequent)
        yield self.reply_ok(msg, response, {})

    @defer.inlineCallbacks
    def list_resources(self, content, headers, msg):
        org = headers['receiver-name']
        log.info('listing resources for ' + org)
        vars=self.governance_support.list(AGENT_NAME+'_facts','contributed','($user,$resource,$action,'+org+')')
        response=[]
        for var in vars:
            response.append([var['user'],var['resource'],var['action']])
        yield self.reply_ok(msg, response, {})

    @defer.inlineCallbacks
    def list_users(self, content, headers, msg):
        org=headers['receiver-name']
        log.info('listing users in ' + org)
        vars=self.governance_support.list(AGENT_NAME+'_facts','enrolled','($user,$role,'+org+')')
        response=[]
        for var in vars:
            response.append([var['user'],var['role']])
        yield self.reply_ok(msg, response, {})

    @defer.inlineCallbacks
    def validate_token(self, content, headers, msg):
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
    def validate_enrollment(self, content, headers, msg):
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

class OrgAgentServiceClient(AgentServiceClient):
    """
    This service client calls the org_agent service. It
    makes service calls RPC style.
    """
    def __init__(self, proc=None, **kwargs):
        if not 'targetname' in kwargs:
            kwargs['targetname'] = AGENT_NAME
        AgentServiceClient.__init__(self, proc, **kwargs)

    @defer.inlineCallbacks
    def request(self, op, headers=None):
        yield self._check_init()
        (content, headers, msg) = yield self.rpc_send(op,headers['content'],headers)
        defer.returnValue(content)


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
