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
from ion.core.intercept.governance_support import GovernanceSupport

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
        self.governance_support = GovernanceSupport(AGENT_NAME)




    @defer.inlineCallbacks
    def op_org_request(self, content, headers, msg):
        op=content['op']
        headers={'receiver-name':content['receiver-name'], 'op':op, 'content':content['content'], 'user-id':headers['user-id']}
        self.store(op, [headers['user-id'], content['receiver-name'], str(content['content'])])
        
        try:
            oasc = OrgAgentServiceClient()
            response = yield oasc.request(op,headers)
        except Exception as exception:
            #if org agent does not respond, store the fact
            response={'belief':'refused','consequent':[op,[headers['user-id'], content['receiver-name'], str(content['content'])]]}

        self.store(response['belief'],response['consequent'])
        if response['belief']=='eject':
            yield response
        else:
            yield self.reply_ok(msg, response, {})

    @defer.inlineCallbacks
    def op_resource_request(self, content, headers, msg):

        #generate header for the message to the resource agent
        op=content['op']
        headers={'receiver-name':content['receiver-name'], 'op':op, 'content':content['content'], 'user-id':headers['user-id']}
        #store the fact that you attempted the request
        #belief('request', 'enroll','shenrie', 'SCILAB', {'role':'researcher'})
        self.store(op, [headers['user-id'], content['receiver-name'], str(content['content'])])
        try:
            #make request to the resource agent
            rasc = ResourceAgentServiceClient()
            response = yield rasc.request(op,headers)
            self.store(response['belief'],response['consequent'])
        except Exception as exception:
            #if resource agent does not respond store the fact
            response={'belief':'refused','consequent':[op,headers['user-id'], content['receiver-name'], str(content['content'])]}
            self.store(response['belief'],response['consequent'])

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

    def check_pending_sanctions(self, content, headers, msg):
        #check the normative filter for obligation
        log.info('applying normative filter')
        try:
            #consequent example: ('make_request', 'escalate', 'shenrie', 'SCILAB', ('sanction', 'SAN1'))
            consequent= self.governance_support.check_pending_sanctions(headers)
            log.debug('consequent in NF is '+str(consequent))

            if len(consequent)==4:
                #assumes sanction have consequent that have an operation to be issued by creditor to debtor with parameters
                op,creditor,debtor,parameters=consequent
                parameters=[creditor,debtor,parameters]
            else:
                #consequent has an operation without parameters
                op=consequent
                parameters=None

            #perform the operation op
            response=getattr(self, op)(content, headers, msg, parameters)

        except Exception as exception:
                log.debug(exception)
                response={'resource_id':headers['receiver-name'],'consequent':None}
                log.error('##### NO SANCTIONS APPLIED #####')
        return response

    def escalate(self,content,headers,msg,parameters):
        creditor,debtor,parameters=parameters
        op=parameters[0]

        #override the content with headers information because op_org_request will inspect
        #the content and form a header out of it
        content={'receiver-name':debtor, 'op':op, 'content':parameters, 'user-id':creditor}

        return self.op_org_request(content,headers,msg)


    def store(self,fact_name,arguments):
        self.governance_support.store(AGENT_NAME+'_facts',fact_name,arguments)



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
