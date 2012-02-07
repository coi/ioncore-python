'''
    This provides the actual invocation of pyke rules processing for the agents
    @author Prashant Kediyal
'''

from __future__ import with_statement
import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)
from pyke import knowledge_engine
from pyke import *
from twisted.internet import defer

DROP='drop'


class GovernanceSupport():
    
    agent='temp'
    """
    Example service interface
    """
    def __init__(self, *args, **kwargs):
        log.info('GovernanceSupport.__init__()')
        for agent in args:
            log.info('activating engine for ' + agent)
        self.agent=agent
        self.my_engine = knowledge_engine.engine(__file__)
        self.my_engine.reset()
        self.my_engine.activate(self.agent)

    #invocation.content passed on; seen here as headers
    def communicator(self,headers):

        if 'receiver-name' in headers:
            servicer = headers['receiver-name']
        else:
            return 'inapplicable'
        requester=headers['user-id']
        op=headers['agent-op']

        if self.agent == 'org_agent' or self.agent=='resource_agent' or self.agent=='user_agent':
            try:

                #log.info('updating agent belief to reflect that request was made ')
                self.store(self.agent+'_facts','request', (op, requester, servicer, headers['content']))
                log.debug(self.agent + ' checking ' +requester  +' for .authorization($id,'+requester+','+servicer+',$antecedent,'+op+')')
                vars, plan = self.my_engine.prove_1_goal(self.agent+'.authorization($id,'+requester+','+servicer+',$antecedent,'+op+')')
                antecedent=vars['antecedent']
                id=vars['id']
                log.info('in norm '+id + ' antecedent '+antecedent +' is true thus authorizing '+requester+' to perform ' + op + ' on '+ servicer)

            except Exception as exception:
                log.debug(exception)
                antecedent = DROP
                log.info('no authorization')

        return antecedent

    def check_detached_commitments(self,headers):
        consequents = []
        log.info('headers: ' + str(headers))
        if 'receiver-name' in headers:
            servicer = headers['receiver-name']
        else:
            return 'inapplicable'

        requester=headers['user-id']
        if self.agent == 'org_agent' or self.agent=='resource_agent' or self.agent=='user_agent':
            try:
                log.debug(self.agent + ' checking ' +servicer +' for .detached_commitment($id,'+servicer+','+requester+',$antecedent,$consequent) to ' + requester)
                with self.my_engine.prove_goal(self.agent+'.detached_commitment($id,'+servicer+','+requester+',$antecedent,$consequent)') as gen:
                    for vars, plan in gen:
                        #vars, plan = my_engine.prove_1_goal(self.agent+'.authorization($id,'+user_id+','+resource_id+','+op+',$response)')
                        consequent=vars['consequent']
                        consequents.append(consequent)
                        id=vars['id']
                        antecedent=vars['antecedent']
                        log.info(id + ' commits '+servicer+'\'s agent to do ' + str(consequent) +' if '+ requester+'\'s agent does '+ str(antecedent))
            except Exception as exception:
                log.debug(exception)
                consequents.append(DROP)
                log.info('no commitments')

        return consequents



    def check_pending_sanctions(self,headers):
        consequents=[]
        log.info('check pending sanctions headers: ' + str(headers) +' in '+self.agent)
        if 'receiver-name' in headers:
            resource_id = headers['receiver-name']
        else:
            return 'inapplicable'

        user_id=headers['user-id']

        consequent='null'
        if self.agent == 'org_agent' or self.agent=='resource_agent' or self.agent=='user_agent':
            try:
                log.debug(self.agent + ' checking ' +resource_id +' for .pending_sanction($id,'+user_id+','+resource_id+',$antecedent,$consequent) to ' + user_id)
                with self.my_engine.prove_goal(self.agent+'.pending_sanction($id,'+user_id+',$creditor,$antecedent,$consequent)') as gen:
                    for var, plan in gen:
                        consequents.append(vars['consequent'])
                        id=vars['id']
                        antecedent=vars['antecedent']
                        log.info(id + ' requires '+resource_id+'\'s agent to carry out sanction ' + str(consequent) +' since '+ user_id+'\'s agent '+ str(antecedent))
            except Exception as exception:
                log.debug(exception)
                consequents.append(DROP)
                log.info('no commitments')

        return consequents

    def store(self,kb_name,fact_name,arguments):
        log.debug('storing in '+kb_name+' '+fact_name+' '+str(arguments))
        #example my_engine.add_universal_fact(org_agent_facts,'enrolled', [headers['user-id'], content['role'], headers['receiver-name']])
        self.my_engine.add_universal_fact(kb_name, fact_name, arguments)
        #my_engine.assert_(kb_name, fact_name, arguments)
        log.info('stored ' +fact_name + str(arguments)+ ' in ' + kb_name)

    def store_universal_fact(self,kb_name,fact_name,arguments):
        #example my_engine.add_universal_fact(org_agent_facts,'enrolled', [headers['user-id'], content['role'], headers['receiver-name']])
        self.my_engine.assert_(kb_name, fact_name, arguments)
        #dump_specific_facts(kb_name)
        log.info('stored ' +fact_name + str(arguments)+ ' in ' + kb_name)


    def dump_universal_facts(self,kb_name):
        return self.my_engine.get_kb(kb_name).dump_universal_facts()

    def dump_specific_facts(self,kb_name):
        return self.my_engine.get_kb(kb_name).dump_specific_facts()

    def list(self,kb_name,fact_name,arguments):
        log.info('listing facts ' + kb_name+'.'+fact_name+arguments)
        response=[]
        with self.my_engine.prove_goal(kb_name+'.'+fact_name+arguments) as gen:
            for vars, plan in gen:
                log.info(str(vars))
                response.append(vars)
        return response

