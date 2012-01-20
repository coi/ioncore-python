#!/usr/bin/env python

"""
@file ion/agent/intelligent/ressource_agent.py
@author Prashant Kediyal
@brief An example service definition that can be used as template.
"""

import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)
from twisted.internet import defer

from ion.core.process.process import ProcessFactory
from ion.core.process.service_process import ServiceProcess, ServiceClient
from ion.core.intercept.governance_support import GovernanceSupport
import random
AGENT_NAME='resource_agent'
DROP='drop'

class ResourceAgentService(ServiceProcess):
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
        log.info('ResourceAgentService.__init__()')

    def slc_init(self):
        # Service life cycle state. Initialize service here. Can use yields.
        self.governance_support = GovernanceSupport(AGENT_NAME)
        
    @defer.inlineCallbacks
    def op_negotiate_resource(self,content,headers,msg):
        response=self.normative_filter(content,headers,msg)
        yield self.reply_ok(msg, response, {})

    @defer.inlineCallbacks
    def op_get_temp(self, content, headers, msg):
        response=self.normative_filter(content,headers,msg)
        yield self.reply_ok(msg, response, {})

    def normative_filter(self, content, headers, msg):
        #check the normative filter for obligation
        log.info('applying normative filter')
        try:
            #consequent= yield self.governance_support.normative_filter(headers)
            consequent= self.governance_support.normative_filter(headers)
            #consequent example: (norm,(commitment,(COM3,(request,get_temp,shenrie,glider55),get_temp)))
            #commitment example: norm(commitment, COM1, glider55, shenrie, antecedent, consequent)
            log.debug('consequent in NF is '+str(consequent))
            if len(consequent)==2:
                op,parameters=consequent
            else:
                op=consequent
                parameters=None

            response=getattr(self, op)(content, headers, msg, parameters)
        except Exception as exception:
                log.debug(exception)
                response={'resource_id':headers['receiver-name'],'consequent':None}
                log.info('##### NO COMMITMENT')

        #yield self.reply_ok(msg, response, {})
        return response

    def norm(self,content,headers,msg,parameters):

        #parameters example: (commitment,COM3,(request,get_temp,shenrie,glider55),get_temp)
        # norm example: norm('commitment', 'COM3', 'glider55', 'shenrie', ('request', 'get_temp', 'shenrie', 'glider55'), 'get_temp')
        norm_type,id,antecedent,consequent=parameters
        debtor=headers['receiver-name']
        creditor=headers['user-id']
        response={'resource_id':debtor,'consequent':None}
        try:
            norm=[norm_type,id, debtor, creditor,antecedent,consequent]
            self.store('norm',norm)
            response={'resource_id':debtor,'event':'norm','consequent':norm}
        except Exception as exception:
            log.debug(exception)
            log.error('SEVERE ERROR; Failed to create norm as indicated by consequent')
        return response


    def get_temp(self, content, headers, msg, temperature):
        response= {'resource_id':headers['receiver-name'],'event':'get_temp','consequent':['temperature on '+headers['receiver-name']+ ' is 8 degree fahrenheit']}
        log.debug('returning ' +str(response))
        #self.store('get_temp',[temperature])
        return response



    def store(self,fact_name,arguments):
        self.governance_support.store(AGENT_NAME+'_facts',fact_name,arguments)


class ResourceAgentServiceClient(ServiceClient):
    """
    This is an exemplar service client that calls the resource agent service. It
    makes service calls RPC style.
    """
    def __init__(self, proc=None, **kwargs):
        #print proc + 'helloSC kwargs are' + kwargs
        if not 'targetname' in kwargs:
            kwargs['targetname'] = AGENT_NAME
        ServiceClient.__init__(self, proc, **kwargs)

    @defer.inlineCallbacks
    def request(self, op, headers=None):
        yield self._check_init()
        (content, headers, msg) = yield self.rpc_send(op,headers['content'],headers)
        defer.returnValue(content)
    
    def request_deferred(self, text='Hi there requester'):
        return self.rpc_send('execute_request', text)

# Spawn of the process using the module name
factory = ProcessFactory(ResourceAgentService)



"""
from ion.play import resource_agent as r
spawn(r)

# TODO:
# supervisor process is #1, our resource_agent should be #2.
# sending to 1 results in a callback with no data, sending to 2 does not
# ever call back.
send(1, {'op':'helloresource','content':'Hello you there resource!'})

from ion.play.hello_service import HelloServiceClient
hc = ResourceAgentServiceClient()
hc.hello()
"""
