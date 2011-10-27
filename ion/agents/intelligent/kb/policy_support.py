'''
    This provides the actual invocation of pyke rules processing for the agents
    @author Prashant Kediyal
'''

from __future__ import with_statement
import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)
from pyke import knowledge_engine,  goal

# Compile and load .krb files in same directory that I'm in (recursively).
engine = knowledge_engine.engine(__file__)


def check(headers):
    '''
        This function runs the forward-chaining example (fc_example.krb).
    '''
    
    org=headers['content']['org']
    user_id=headers['user-id']
    resource_id = headers['content']['resource_id']
    op=headers['content']['op']
    agent=headers['receiver'].split(".")[1]
    engine.reset()      # Allows us to run tests multiple times.

    engine.activate(agent)  # Runs all applicable forward-chaining rules.
    
    if agent=='useragent':
        try: 
            log.debug('useragents policy being applied')
            vars, plan = engine.prove_1_goal(agent+'.authorized_user('+org+','+user_id+',$role)')
        except:
            return 'denied'
            log.info('permission: ' + 'denied')
        else:
            log.info('role for user_id is ' + vars['role'])
    else:
        role=headers['content']['role']
        try: 
            vars, plan = engine.prove_1_goal(agent+'.authorized_resource('+org+','+role+','+resource_id+','+op+',$permission)')
        except:
            return 'denied'
            log.info('permission: ' + 'denied')
        else:
            log.info(vars)
        
    return vars