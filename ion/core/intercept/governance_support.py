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
<<<<<<< .merge_file_VcZwT7
=======

>>>>>>> .merge_file_TOAa21

class GovernanceSupport():

    agent='temp'
    """
    Example service interface
    """
    def __init__(self, *args, **kwargs):
        log.info('GovernanceSupport.__init__()')
        self.my_engine = knowledge_engine.engine(__file__)
        
        for agent in args:
            log.info('activating engine for ' + agent)
        self.agent=agent
<<<<<<< .merge_file_VcZwT7
=======
        self.my_engine = knowledge_engine.engine(__file__)
>>>>>>> .merge_file_TOAa21
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

<<<<<<< .merge_file_VcZwT7
        user_id=headers['user-id']
        org='ooi'
        subjectRoles=['researcher']
        op=headers['op']
        permission='null'
        #self.my_engine.reset()
        #self.my_engine.activate(self.agent)
        # Runs all applicable forward-chaining rules.
        #log.info(agent + ' checks Governance applied on ' + user_id + ' '+ org + ' ' + str(subjectRoles) + ' '+ resource_id + ' '+ op + ' '+ agent)
        if self.agent == 'org_agent' or self.agent=='resource_agent' or self.agent=='user_agent':
            try:
                log.debug('##### ')
                log.debug('##### ')
                log.debug('##### ')
                log.debug('##### '+self.agent + ' checking ' +user_id + str(subjectRoles) +' for .authorization($id,'+user_id+','+resource_id+','+op+',$consequent)')
                vars, plan = self.my_engine.prove_1_goal(self.agent+'.authorization($id,'+user_id+','+resource_id+','+op+',$consequent)')
                permission=vars['consequent']
=======
        if self.agent == 'org_agent' or self.agent=='resource_agent' or self.agent=='user_agent':
            try:

                #log.info('updating agent belief to reflect that request was made ')
                log.debug(self.agent + ' checking ' +requester  +' for .authorization($id,'+requester+','+servicer+',$antecedent,'+op+')')
                vars, plan = self.my_engine.prove_1_goal(self.agent+'.authorization($id,'+requester+','+servicer+',$antecedent,'+op+')')
                antecedent=vars['antecedent']
>>>>>>> .merge_file_TOAa21
                id=vars['id']
                log.info('in norm '+id + ' antecedent '+antecedent +' is true thus authorizing '+requester+' to perform ' + op + ' on '+ servicer)
                self.store(self.agent+'_facts','request', (op, requester, servicer, headers['content']))
            except Exception as exception:
                log.debug(exception)
<<<<<<< .merge_file_VcZwT7
                permission = DROP
                log.info('##### no authorization')
                #try:
                #    log.debug('#####'+'checking authorization')
                #    vars, plan = self.my_engine.prove_1_goal(self.agent+'.authorization('+resource_id+','+user_id+','+op+',$response)')
                #    permission=vars['response']
                #    log.info('#####'+self.agent+' has authorization to ' + permission)
                #except:
                #    log.info('#####'+'no authorization')
            log.debug('#####')
            log.debug('#####')
            log.debug('#####')
        return permission
=======
                antecedent = DROP
                log.info('no authorization')

        return antecedent
>>>>>>> .merge_file_TOAa21

    def check_detached_commitments(self,headers):
        consequents = []
        log.debug('headers: ' + str(headers))
        if 'receiver-name' in headers:
            servicer = headers['receiver-name']
        else:
            return 'inapplicable'

<<<<<<< .merge_file_VcZwT7
        user_id=headers['user-id']
        org='ooi'
        subjectRoles=['researcher']
        op=headers['op']
        #self.agent=headers['receiver'].split(".")[1]
        consequent='null'
        #self.my_engine.reset()
        #self.my_engine.activate(self.agent)
        if self.agent == 'org_agent' or self.agent=='resource_agent' or self.agent=='user_agent':
            try:
                log.debug('##### '+self.agent + ' checking ' +resource_id +' for .commitment($id,'+resource_id+','+user_id+',$antecedent,$consequent) to ' + user_id)
                #vars, plan = self.my_engine.prove_1_goal(self.agent+'.violated_commitment($id,'+resource_id+','+user_id+','+op+',$response)')
                vars, plan = self.my_engine.prove_1_goal(self.agent+'.detached_commitment($id,'+resource_id+','+user_id+',$antecedent,$consequent)')
                #vars, plan = self.my_engine.prove_1_goal(self.agent+'.authorization($id,'+user_id+','+resource_id+','+op+',$response)')
                consequent=vars['consequent']
                id=vars['id']
                antecedent=vars['antecedent']
                log.info('##### '+id + ' commits '+resource_id+'\'s agent to do ' + str(consequent) +' if '+ user_id+'\'s agent does '+ str(antecedent))
=======
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
>>>>>>> .merge_file_TOAa21
            except Exception as exception:
                log.error(exception)
                consequents.append(DROP)
                log.info('no commitments')

        return consequents



    def check_pending_sanctions(self,headers):
        consequents=[]
        log.debug('check pending sanctions headers: ' + str(headers) +' in '+self.agent)
        if 'receiver-name' in headers:
            resource_id = headers['receiver-name']
        else:
            return 'inapplicable'

        user_id=headers['user-id']
<<<<<<< .merge_file_VcZwT7
        org='ooi'
        subjectRoles=['researcher']
        op=headers['op']
        #agent=headers['receiver'].split(".")[1]
        #self.my_engine.reset()
        #self.my_engine.activate(self.agent)

        consequent='null'
        if self.agent == 'org_agent' or self.agent=='resource_agent' or self.agent=='user_agent':
            try:
                log.debug('##### '+self.agent + ' checking ' +resource_id +' for .pending_sanction($id,'+user_id+','+resource_id+',$antecedent,$consequent) to ' + user_id)
                #vars, plan = self.my_engine.prove_1_goal(self.agent+'.violated_commitment($id,'+resource_id+','+user_id+','+op+',$response)')
                vars, plan = self.my_engine.prove_1_goal(self.agent+'.pending_sanction($id,'+user_id+',$creditor,$antecedent,$consequent)')
                #vars, plan = self.my_engine.prove_1_goal(self.agent+'.authorization($id,'+user_id+','+resource_id+','+op+',$response)')
                consequent=vars['consequent']
                id=vars['id']
                antecedent=vars['antecedent']
                log.info('##### '+id + ' requires '+resource_id+'\'s agent to carry out sanction ' + str(consequent) +' since '+ user_id+'\'s agent '+ str(antecedent))
=======

        if self.agent == 'org_agent' or self.agent=='resource_agent' or self.agent=='user_agent':
            try:
                log.debug(self.agent + ' checking ' +resource_id +' for .pending_sanction($id,'+user_id+','+resource_id+',$antecedent,$consequent) to ' + user_id)
                with self.my_engine.prove_goal(self.agent+'.pending_sanction($id,'+user_id+',$creditor,$antecedent,$consequent)') as gen:
                    for vars, plan in gen:
                        consequent=vars['consequent']
                        consequents.append(consequent)
                        id=vars['id']
                        antecedent=vars['antecedent']
                        log.info(id + ' requires '+resource_id+'\'s agent to carry out sanction ' + str(consequent) +' since '+ user_id+'\'s agent '+ str(antecedent))
                    log.info(self.agent+': no more sanctions')
>>>>>>> .merge_file_TOAa21
            except Exception as exception:
                log.debug(exception)
                consequents.append(DROP)
                log.info(self.agent+': no sanctions')

        return consequents

    def store(self,kb_name,fact_name,arguments):
        log.debug('storing in '+kb_name+' '+fact_name+' '+str(arguments))
<<<<<<< .merge_file_VcZwT7
        #example self.my_engine.add_universal_fact(org_agent_facts,'enrolled', [headers['user-id'], content['role'], headers['receiver-name']])
        self.my_engine.add_universal_fact(kb_name, fact_name, arguments)
        #self.my_engine.assert_(kb_name, fact_name, arguments)
        log.info('stored ' +fact_name + str(arguments)+ ' in ' + kb_name)

    def store_universal_fact(self,kb_name,fact_name,arguments):
        #example self.my_engine.add_universal_fact(org_agent_facts,'enrolled', [headers['user-id'], content['role'], headers['receiver-name']])
=======
        #example my_engine.add_universal_fact(org_agent_facts,'enrolled', [headers['user-id'], content['role'], headers['receiver-name']])
        self.my_engine.add_universal_fact(kb_name, fact_name, arguments)
        #my_engine.assert_(kb_name, fact_name, arguments)
        log.info('stored ' +fact_name + str(arguments)+ ' in ' + kb_name)

    def store_universal_fact(self,kb_name,fact_name,arguments):
        #example my_engine.add_universal_fact(org_agent_facts,'enrolled', [headers['user-id'], content['role'], headers['receiver-name']])
>>>>>>> .merge_file_TOAa21
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

