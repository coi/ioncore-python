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
from ion.core.process.service_process import ServiceProcess
from ion.agents.intelligent.resource_agent import ResourceAgentServiceClient
from ion.agents.intelligent.org_agent import OrgAgentServiceClient
from ion.core.intercept.governance_support import GovernanceSupport
from collections import deque


class AgentServiceProcess(ServiceProcess):

    def slc_init(self):
        # Service life cycle state. Initialize service here. Can use yields.
        if  self.AGENT_NAME == None:
            self.AGENT_NAME==self.__name__
        self.governance_support = GovernanceSupport(self.AGENT_NAME)

    @defer.inlineCallbacks
    def op_perform_obligations(self, content, headers, msg):
        #check for obligations
        log.info('performing obligations')
        self.store(content['op'], [headers['user-id'], content['receiver-name'], content['content']])

        response_queue = deque()
        try:
            consequents=self.governance_support.check_detached_commitments(headers)
            log.debug('consequents from detached commitment are '+str(consequents))
            for consequent in consequents:
                #for parameterized consequents
                if len(consequent)==2:
                    op,parameters=consequent
                elif len(consequent)==1 :
                    #non parameterized consequents
                    op=consequent
                    parameters=None
                else :
                    op==None
                    log.error('Error in the way consequent has been declared'+str(consequent))
                if op!=None:
                    response=getattr(self, op)(content, headers, msg, parameters)
                if response !=None:
                    self.store(response)
                response_queue.append(response)
        except Exception as exception:
                log.debug(exception)
                response_queue.append(exception)

        yield self.reply_ok(msg, response_queue, {})

    def apply_sanctions(self, content, headers, msg):
        #check for pending_sanctions
        log.info('checking for sanctions')
        response_queue = deque()
        try:
            #consequent example: ('make_request', 'escalate', 'shenrie', 'SCILAB', ('sanction', 'SAN1'))
            consequents= self.governance_support.check_pending_sanctions(headers)
            log.debug('consequents of applicable sanctions are '+str(consequents))
            for consequent in consequents:
                if len(consequent)==4:
                    #assumes sanction have consequent that have an operation to be issued by creditor to debtor with parameters
                    op,creditor,debtor,parameters=consequent
                    parameters=[creditor,debtor,parameters]
                elif len(consequent)==1:
                    #consequent has an operation without parameters
                    op=consequent
                    parameters=None
                else :
                    op==None
                    log.error('Error in the way consequent has been declared'+str(consequent))
                if op!=None:
                    #perform the operation op
                    response=getattr(self, op)(content, headers, msg, parameters)
                if response !=None:
                    self.store(response)
                response_queue.append(response)
        except Exception as exception:
                log.debug(exception)
                response_queue.append(exception)

        yield self.reply_ok(msg, response_queue, {})

    #sometimes the consequent may simply be creation of another norm
    def norm(self,content,headers,msg,parameters):
        #parameters example: (commitment,COM3,(request,get_temp,shenrie,glider55),get_temp)
        # norm example: norm('commitment', 'COM3', 'glider55', 'shenrie', ('request', 'get_temp', 'shenrie', 'glider55'), 'get_temp')
        response=None
        try:
            norm_type,id,antecedent,consequent=parameters
            debtor=headers['receiver-name']
            creditor=headers['user-id']
            norm=[norm_type,id, debtor, creditor,antecedent,consequent]
            response=['norm',norm]
        except Exception as exception:
            log.debug(exception)
            log.error('SEVERE ERROR; Failed to create norm ' + str(parameters))
        return response
    @defer.inlineCallbacks
    def escalate(self,content,headers,msg,parameters):
        creditor,debtor,parameters=parameters
        op=parameters[0]
        #override the content with headers information because op_org_request will inspect
        #the content and form a header out of it
        headers={'receiver-name':debtor, 'op':op, 'content':parameters, 'user-id':creditor}
        response=None
        try:
            oasc = OrgAgentServiceClient()
            response = yield oasc.request(op,headers)
        except Exception as exception:
            log.error(exception)
            log.error('SEVERE ERROR; Failed to escalate ' + str(parameters))
        yield response


    def store(self,fact_name,arguments):
        self.governance_support.store(self.AGENT_NAME+'_facts',fact_name,arguments)




class AgentClient(ServiceClient):
    """
    This is the base class for service client libraries. Service client libraries
    can be used from any process or standalone (in which case they spawn their
    own client process). A service client makes accessing the service easier and
    can perform client side optimizations (such as caching and transformation
    of certain service results).
    """

    def does_service_exist(self, name):
        """The existence of a queue with the name of the service is
        equivalent to the service existing.
        """
        super.__self__.proc.container.name_exists(name, scope='system')


    #@defer.inlineCallbacks
    def rpc_send(self, op, content,headers=None):
        log.debug('this rpc_send is called')
        return ServiceClient.rpc_send(self,'perform_obligations',content,headers)