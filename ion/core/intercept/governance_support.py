'''
    This provides the actual invocation of pyke rules processing for the agents
    @author Prashant Kediyal
'''

from __future__ import with_statement
import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)
from pyke import *
from twisted.internet import defer

DROP='drop'
my_engine = knowledge_engine.engine(__file__)
        

class GovernanceSupport(object):
    """
    Example service interface
    """
    gov_engine=my_engine
    def __init__(self, *args, **kwargs):
        log.info('GovernanceSupport.__init__()')
        my_engine.reset()
        my_engine.activate('org_agent')

    def checks(self,headers):
        user_id=headers['user-id']
        org='ooi'
        subjectRoles=subjectRoles=['researcher']
        resource_id = headers['receiver-name']
        op=headers['op']
        agent=headers['receiver'].split(".")[1]

        # Runs all applicable forward-chaining rules.
        log.info('Governance applied on ' + user_id + ' '+ org + ' ' + str(subjectRoles) + ' '+ resource_id + ' '+ op + ' '+ agent)
        if agent == 'org_agent':
            try:
                log.debug('checking if empowered')
                vars, plan = my_engine.prove_1_goal(agent+'.power('+resource_id+','+user_id+','+op+',$response)')
                permission=vars['response']
                log.info('org has power to ' + permission)
            except:
                permission = DROP
                log.info('no power')
                try:
                    log.debug('checking authorization')
                    vars, plan = my_engine.prove_1_goal(agent+'.authorization('+resource_id+','+user_id+','+op+',$response)')
                    permission=vars['response']
                    log.info('org has authorizatoin to ' + permission)
                except:
                    log.info('no authorization')


        return permission

    def store(self,kb_name,fact_name,arguments):
        log.info('storing ' +fact_name + ' ('+str(arguments)+') ' + 'in ' + kb_name)
        #my_engine.add_universal_fact(kb_name, fact_name, arguments)
        my_engine.assert_(kb_name, fact_name, arguments)
        log.info('stored ' +fact_name + str(arguments))

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

