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
        my_engine.activate('orgagent')

    def checks(self,msg):
        '''
            This function runs the forward-chaining example (fc_example.krb).
        '''
        user_id=msg['content']['user_id']
        org=msg['content']['org']
        role=msg['content']['role']
        resource_id = msg['content']['resource_id']
        op=msg['content']['op']
        agent=msg['receiver'].split(".")[1]
        response=DROP
          # Runs all applicable forward-chaining rules.
        log.info('Governance applied on ' + user_id + ' '+ org + ' ' + str(role) + ' '+ resource_id + ' '+ op + ' '+ agent)
        if agent == 'orgagent':
            try:
                log.debug('orgagent governance being applied')
                vars, plan = my_engine.prove_1_goal(agent+'.power('+resource_id+','+user_id+','+op+',$response)')
                response=vars['response']
                #vars, plan = engine.prove_1_goal(agent+'.has_authorization('+org+','+user_id+',$role)')
                #vars, plan = engine.prove_1_goal(agent+'.has_commitment('+org+','+user_id+',$role)')
                #vars, plan = engine.prove_1_goal(agent+'.has_sanction('+org+','+user_id+',$role)')
                #vars, plan = engine.prove_1_goal(agent+'.has_prohibition('+org+','+user_id+',$role)')
            except:
                response = DROP
                log.info('permission: ' + 'denied')
            else:
                log.info('governance response is ' + response)
                msg['content']['governance_response'] = response


        elif agent=='useragent':
            '''try:
                log.debug('useragents governance being applied')
                vars, plan = engine.prove_1_goal(agent+'.authorized_user('+org+','+user_id+',$role)')
            except:
                return 'denied'
                log.info('permission: ' + 'denied')
            else:
                log.info('role for user_id is ' + vars['role'])'''
        elif agent == 'resourceagent':
            '''role=str(msg['content']['role'])
            try:
                vars, plan = engine.prove_1_goal(agent+'.authorized_resource('+org+','+role+','+resource_id+','+op+',$permission)')
            except:
                return 'denied'
                log.info('permission: ' + 'denied')
            else:
                log.info(vars)'''
        else :
            '''role=str(msg['content']['role'])
            try:
                vars, plan = engine.prove_1_goal(agent+'.authorized_resource('+org+','+role+','+resource_id+','+op+',$permission)')
            except:
                return 'denied'
                log.info('permission: ' + 'denied')
            else:
                log.info(vars)'''
            print 'i am here !!'

        return response 

    def hi(self, name):
        print "hi " + name

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

