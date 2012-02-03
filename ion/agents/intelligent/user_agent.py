#!/usr/bin/env python

"""
@file ion/play/user_agent_service.py
@author Prashant Kediyal
@brief An example service definition that can be used as template.
"""

import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)


from twisted.internet import defer

from ion.core.process.process import ProcessFactory
from ion.agents.intelligent.resource_agent import ResourceAgentServiceClient
from ion.agents.intelligent.org_agent import OrgAgentServiceClient
from ion.core.agents.agent_service_process import AgentServiceProcess, AgentServiceClient


AGENT_NAME='user_agent'

class UserAgentService(AgentServiceProcess):
    """
    Example service interface
    """
    # Declaration of service
    declare = AgentServiceProcess.service_declare(name=AGENT_NAME,
                                             version='0.1.0',
                                             dependencies=[])
    def __init__(self, *args, **kwargs):
        self.AGENT_NAME=AGENT_NAME
        # Service class initializer. Basic config, but no yields allowed.
        AgentServiceProcess.__init__(self, *args, **kwargs)
        log.info('UserAgentService.__init__()')




    @defer.inlineCallbacks
    def op_org_request(self, content, headers, msg,requester,servicer,parameters):

        #(parameters=(enroll,(student))))
        op,parameters=parameters
        #todo take off the op parameter below
        headers={'op':op,'agent-op':op,'user-id':requester,'receiver-name':servicer,'content':parameters}

        try:
            oasc = OrgAgentServiceClient()
            # response returned should be (enroll,(shenrie,SCILAB,student))
            response = yield oasc.request(op,headers)
        except Exception as exception:
            #if org agent does not respond, store the fact
            #response={'belief':'refused','consequent':[op,[headers['user-id'], content['receiver-name'], str(content['content'])]]}
            response=None

        yield response


    @defer.inlineCallbacks
    def op_resource_request(self, content, headers, msg, parameters):

        #generate header for the message to the resource agent
        op=content['agent-op']
        headers={'receiver-name':content['receiver-name'], 'op':op, 'content':content['content'], 'user-id':headers['user-id']}
        #store the fact that you attempted the request
        #belief('request', 'enroll','shenrie', 'SCILAB', {'role':'researcher'})
        try:
            #make request to the resource agent
            rasc = ResourceAgentServiceClient()
            response = yield rasc.request(op,headers)
            self.store(response['belief'],response['consequent'])
        except Exception as exception:
            #if resource agent does not respond store the fact
            response={'belief':'refused','consequent':[op,headers['user-id'], content['receiver-name'], str(content['content'])]}

            #check if there is a sanction for an unexpected response
            log.info('No response received from the resource agent, checking for applicable sanctions')

            consequent=self.check_pending_sanctions(content,headers,msg)
               
            #try:
            #    if len(consequent)==2:
            #        op,parameters=consequent
            #    else:
            #        op=consequent
            #        parameters=None
            #    response=getattr(self, op)(content, headers, msg, parameters)
            #    if response is not None or response['belief'] is not None:
            #        self.store(response['belief'],response['consequent'])
            #except Exception as exception:
            #    log.error(exception)
            #    response='Failure'



        yield self.reply_ok(msg, response, {})





class UserAgentServiceClient(AgentServiceClient):
    """
    This service client calls the user_agent service. It
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
