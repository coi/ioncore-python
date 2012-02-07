#!/usr/bin/env python

"""
@file ion/play/user_agent_service.py
@author Prashant Kediyal
@brief The base Agent class that must be extended to build agents
"""

import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)


from twisted.internet import defer

from ion.core.process.service_process import ServiceProcess, ServiceClient
from ion.core.intercept.governance_support import GovernanceSupport
from ion.core.intercept.policy_support import PolicySupport

class AgentServiceProcess(ServiceProcess):

    def slc_init(self):
        # Service life cycle state. Initialize service here. Can use yields.
        if  self.AGENT_NAME == None:
            log.warn('No agent name')
            self.AGENT_NAME==(self.__name__).rsplit('.',1)[1]
            log.warn('using '+self.AGENT_NAME+' instead')
        self.governance_support = GovernanceSupport(self.AGENT_NAME)
        self.policy_support=PolicySupport()




    @defer.inlineCallbacks
    def op_process_request(self,content,headers,msg):
        #self.reply_ok(msg, 'LATER ALLIGATOR', {})

        responses = []
        if headers['performative']!='request':
            log.info(headers['performative'])
        else:
            responses=yield self.perform_obligations(content, headers, msg)
            log.info(self.AGENT_NAME +': applying sanctions')
            #results=yield self.apply_sanctions(content, headers, msg)
            #responses.extend(results)
            #yield self.reply_ok(msg, responses, {})
            log.info(self.AGENT_NAME + ': returning '+str(responses))
        self.reply_ok(msg, responses, {})
        #defer.returnValue(responses)

    @defer.inlineCallbacks
    def perform_obligations(self, content, headers, msg):

        responses = []
        try:
            consequents=self.governance_support.check_detached_commitments(headers)
            for consequent in consequents:
                #for parameterized consequents
                if len(consequent)==4:
                    op,requester,servicer,parameters=consequent
                elif len(consequent)==1 :
                    #non parameterized consequents
                    op=consequent
                    parameters=None
                else :
                    log.error(self.AGENT_NAME +': Error in the way consequent has been declared '+consequent+ ' its length is '+str(len(consequent)))

                if op == None:
                    log.error(self.AGENT_NAME +': Error in the way consequent has been declared'+str(consequent))
                if op != None:
                    #expects a list of results
                    results = yield getattr(self, op)(content, headers, msg, requester,servicer,parameters)
                    log.info(self.AGENT_NAME+' response '+str(results))
                if results != None:
                    for result in results:
                        try:
                            predicate,parameters=result
                            self.store(predicate,parameters)
                        except Exception as exception:
                            log.error(exception)

                    responses.extend(results)
            log.info(self.AGENT_NAME +': No more obligations')
        except Exception as exception:
                log.debug(exception)
                responses.append(exception)
        defer.returnValue(responses)


    @defer.inlineCallbacks
    def perform_sanctions(self, content, headers, msg):

        responses = []
        try:
            consequents=self.governance_support.check_pending_sanctions(headers)
            for consequent in consequents:
                #for parameterized consequents
                if len(consequent)==4:
                    op,requester,servicer,parameters=consequent
                elif len(consequent)==1 :
                    #non parameterized consequents
                    op=consequent
                    parameters=None
                else :
                    log.error(self.AGENT_NAME +': Error in the way consequent has been declared '+consequent+ ' its length is '+str(len(consequent)))

                if op == None:
                    log.error(self.AGENT_NAME +': Error in the way consequent has been declared'+str(consequent))
                if op != None:
                    #expects a list of results
                    results = yield getattr(self, op)(content, headers, msg, requester,servicer,parameters)
                    log.info(self.AGENT_NAME+' response '+str(results))
                if results != None:
                    for result in results:
                        try:
                            predicate,parameters=result
                            self.store(predicate,parameters)
                        except Exception as exception:
                            log.error(exception)

                    responses.extend(results)
            log.info(self.AGENT_NAME +': No more sanctions')
        except Exception as exception:
                log.debug(exception)
                responses.append(exception)
        defer.returnValue(responses)

    def apply_sanctionss(self, content, headers, msg):
        #check for pending_sanctions
        log.info(self.AGENT_NAME +': checking for sanctions')
        responses = None
        try:
            #consequent example: ('make_request', 'escalate', 'shenrie', 'SCILAB', ('sanction', 'SAN1'))
            consequents= self.governance_support.check_pending_sanctions(headers)
            log.debug(self.AGENT_NAME +': consequents of applicable sanctions are '+str(consequents))
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
                    op == None
                    log.error(self.AGENT_NAME +': Error in the way consequent has been declared'+str(consequent))
                if op != None:
                    #perform the operation op
                    response=getattr(self, op)(content, headers, msg, parameters)
                if response != None:
                    self.store(response)
                responses.append(response)
        except Exception as exception:
                log.debug(exception)
                responses.append(exception)

        return self.reply_ok(msg, responses, {})

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
            log.error(self.AGENT_NAME +': SEVERE ERROR; Failed to create norm ' + str(parameters))
        return response

    


    def store(self,fact_name,arguments):
        self.governance_support.store(self.AGENT_NAME+'_facts',fact_name,arguments)




class AgentServiceClient(ServiceClient):
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


    def rpc_send(self, op, content,headers=None):
        return ServiceClient.rpc_send(self,'process_request',content,headers)

