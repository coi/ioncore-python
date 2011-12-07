'''
    This provides the actual invocation of pyke rules processing for the agents
    @author Prashant Kediyal
'''

from __future__ import with_statement
import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)
from pyke import knowledge_engine,  goal

print str(__name__)
import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)


from twisted.internet import defer

from ion.core.process.process import ProcessFactory
from ion.core.process.service_process import ServiceProcess, ServiceClient
from ion.agents.intelligent.kb import policy_support

# Compile and load .krb files in same directory that I'm in (recursively).
engine = knowledge_engine.engine(__file__)

class GovernanceSupportService(ServiceProcess):
    """
    Example service interface
    """
    # Declaration of service
    declare = ServiceProcess.service_declare(name='governance_support',
                                             version='0.1.0',
                                             dependencies=[])

    def __init__(self, *args, **kwargs):
        # Service class initializer. Basic config, but no yields allowed.
        ServiceProcess.__init__(self, *args, **kwargs)
        log.info('GovernanceSupportService.__init__()')

    def slc_init(self):
        # Service life cycle state. Initialize service here. Can use yields.
        pass

    def hi(self, name):
        print "hi " + name


    @defer.inlineCallbacks
    def op_check(self, request_content, headers, msg):
        log.info('governance check request content: '+str(request_content))
        #policy_response = policy_support.check(headers)
        #if policy_response!='denied':
        #    rasc = ResourceAgentServiceClient()
        #    request_content['role']=policy_response['role']
        #    log.info('request to resource agent '+str(request_content))
        #    policy_response = yield rasc.execute_request(request_content)
        yield self.reply_ok(msg, policy_response, {})

    def checks(msg):
        '''
            This function runs the forward-chaining example (fc_example.krb).
        '''
        print str(msg)
        return
        user_id=msg['content']['user_id']
        org=msg['content']['org']
        role=msg['content']['role']
        resource_id = msg['content']['resource_id']
        op=msg['content']['op']
        agent=msg['receiver'].split(".")[1]
        engine.reset()      # Allows us to run tests multiple times.

        engine.activate(agent)  # Runs all applicable forward-chaining rules.

        if agent == 'orgagents':
            try:
                log.debug('orgagent governance being applied')
                vars, plan = engine.prove_1_goal(agent+'.power('+resource_id+','+user_id+','+op+',$response)')
                #vars, plan = engine.prove_1_goal(agent+'.has_authorization('+org+','+user_id+',$role)')
                #vars, plan = engine.prove_1_goal(agent+'.has_commitment('+org+','+user_id+',$role)')
                #vars, plan = engine.prove_1_goal(agent+'.has_sanction('+org+','+user_id+',$role)')
                #vars, plan = engine.prove_1_goal(agent+'.has_prohibition('+org+','+user_id+',$role)')
            except:
                return 'denied'
                log.info('permission: ' + 'denied')
            else:
                log.info('role for user_id is ' + vars['response'])

        elif agent=='useragent':
            '''try:
                log.debug('useragents governance being applied')
                vars, plan = engine.prove_1_goal(agent+'.authorized_user('+org+','+user_id+',$role)')
            except:
                return 'denied'
                log.info('permission: ' + 'denied')
            else:
                log.info('role for user_id is ' + vars['role'])'''
        if agent == 'resourceagent':
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

        return vars

    def store(headers):
        log.info('store facts ' +str(headers))


class GovernanceSupportServiceClient(ServiceClient):
    """
    This is an exemplar service client that calls the user_agent service. It
    makes service calls RPC style.
    """
    def __init__(self, proc=None, **kwargs):
        if not 'targetname' in kwargs:
            kwargs['targetname'] = "governance_support"
        ServiceClient.__init__(self, proc, **kwargs)


    @defer.inlineCallbacks
    def check(self, request_content=None):
        log.info('Governance check')
        yield self._check_init()
        (request_content, headers, msg) = yield self.rpc_send('check',request_content)
        log.info('Governance Support reply: '+str(request_content))
        defer.returnValue(str(request_content))

# Spawn of the process using the module name
factory = ProcessFactory(GovernanceSupportService)