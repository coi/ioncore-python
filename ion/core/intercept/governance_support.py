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
my_engine = knowledge_engine.engine(__file__)


class GovernanceSupport(object):
    """
    Example service interface
    """
    def __init__(self, *args, **kwargs):
        log.info('GovernanceSupport.__init__()')
        for agent in args:
            log.info('activating engine for ' + agent)
        my_engine.reset()
        my_engine.activate(agent)


    def communicator(self,headers):
        log.info('headers: ' + str(headers))
        if 'receiver-name' in headers:
            resource_id = headers['receiver-name']
        else:
            return 'inapplicable'

        user_id=headers['user-id']
        org='ooi'
        subjectRoles=['researcher']
        op=headers['op']
        agent=headers['receiver'].split(".")[1]
        permission='null'
        my_engine.reset()
        my_engine.activate(agent)
        # Runs all applicable forward-chaining rules.
        #log.info(agent + ' checks Governance applied on ' + user_id + ' '+ org + ' ' + str(subjectRoles) + ' '+ resource_id + ' '+ op + ' '+ agent)
        if agent == 'org_agent' or agent=='resource_agent' or agent=='user_agent':
            try:
                log.debug('##### ')
                log.debug('##### ')
                log.debug('##### ')
                log.debug('##### '+agent + ' checking ' +user_id + str(subjectRoles) +' for .authorization($id,'+user_id+','+resource_id+','+op+',$consequent)')
                vars, plan = my_engine.prove_1_goal(agent+'.authorization($id,'+user_id+','+resource_id+','+op+',$consequent)')
                permission=vars['consequent']
                id=vars['id']
                log.info('##### '+'norm '+id + ' permits '+user_id+' to perform ' + op + ' on '+ resource_id)
                log.info('##### updating agent belief to reflect that request was made ')
                #self.store(agent+'_facts','belief',[ headers['op'], headers['user-id'], headers['receiver-name'],  headers['content']])
                self.store(agent+'_facts',headers['performative'], [headers['op'], headers['user-id'], headers['receiver-name'],  headers['content']])
            except Exception as exception:
                log.debug(exception)
                permission = DROP
                log.info('##### no authorization')
                #try:
                #    log.debug('#####'+'checking authorization')
                #    vars, plan = my_engine.prove_1_goal(agent+'.authorization('+resource_id+','+user_id+','+op+',$response)')
                #    permission=vars['response']
                #    log.info('#####'+agent+' has authorization to ' + permission)
                #except:
                #    log.info('#####'+'no authorization')
            log.debug('#####')
            log.debug('#####')
            log.debug('#####')
        return permission

    def normative_filter(self,headers):
        log.info('headers: ' + str(headers))
        if 'receiver-name' in headers:
            resource_id = headers['receiver-name']
        else:
            return 'inapplicable'

        user_id=headers['user-id']
        org='ooi'
        subjectRoles=['researcher']
        op=headers['op']
        agent=headers['receiver'].split(".")[1]
        consequent='null'
        my_engine.reset()
        my_engine.activate(agent)
        if agent == 'org_agent' or agent=='resource_agent' or agent=='user_agent':
            try:
                log.debug('##### ')
                log.debug('##### ')
                log.debug('##### ')
                log.debug('##### '+agent + ' checking ' +resource_id +' for .commitment($id,'+resource_id+','+user_id+',$antecedent,$consequent) to ' + user_id)
                #vars, plan = my_engine.prove_1_goal(agent+'.violated_commitment($id,'+resource_id+','+user_id+','+op+',$response)')
                vars, plan = my_engine.prove_1_goal(agent+'.violated_commitment($id,'+resource_id+','+user_id+',$antecedent,$consequent)')
                #vars, plan = my_engine.prove_1_goal(agent+'.authorization($id,'+user_id+','+resource_id+','+op+',$response)')
                log.debug('##### HELLO NORM CHECKED')
                consequent=vars['consequent']
                id=vars['id']
                antecedent=vars['antecedent']
                log.info('##### '+id + ' commits '+resource_id+'\'s agent to do ' + str(consequent) +' if '+ user_id+'\'s agent does '+ str(antecedent))
            except Exception as exception:
                log.debug(exception)
                consequent = DROP
                log.info('##### no commitments')
                #try:
                #    log.debug('#####'+'checking authorization')
                #    vars, plan = my_engine.prove_1_goal(agent+'.authorization('+resource_id+','+user_id+','+op+',$response)')
                #    permission=vars['response']
                #    log.info('#####'+agent+' has authorization to ' + permission)
                #except:
                #    log.info('#####'+'no authorization')
            log.debug('#####')
            log.debug('#####')
            log.debug('#####')
        return consequent


    def store(self,kb_name,fact_name,arguments):
        #example my_engine.add_universal_fact(org_agent_facts,'enrolled', [headers['user-id'], content['role'], headers['receiver-name']])
        my_engine.add_universal_fact(kb_name, fact_name, arguments)
        #my_engine.assert_(kb_name, fact_name, arguments)
        log.info('stored ' +fact_name + str(arguments)+ ' in ' + kb_name)

    def store_universal_fact(self,kb_name,fact_name,arguments):
        #example my_engine.add_universal_fact(org_agent_facts,'enrolled', [headers['user-id'], content['role'], headers['receiver-name']])
        my_engine.assert_(kb_name, fact_name, arguments)
        #dump_specific_facts(kb_name)
        log.info('stored ' +fact_name + str(arguments)+ ' in ' + kb_name)


    def dump_universal_facts(self,kb_name):
        return my_engine.get_kb(kb_name).dump_universal_facts()

    def dump_specific_facts(self,kb_name):
        return my_engine.get_kb(kb_name).dump_specific_facts()

    def list(self,kb_name,fact_name,arguments):
        log.info('listing facts ' + kb_name+'.'+fact_name+arguments)
        response=[]
        with my_engine.prove_goal(kb_name+'.'+fact_name+arguments) as gen:
            for vars, plan in gen:
                log.info(str(vars))
                response.append(vars)
        return response

