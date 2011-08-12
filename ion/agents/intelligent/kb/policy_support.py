# $Id: driver.py 6de8ee4e7d2d 2010-03-29 mtnyogi $
# coding=utf-8
# 
# Copyright © 2007-2008 Bruce Frederiksen
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

'''
    This example shows how people are related.  The primary data (facts) that
    are used to figure everything out are in family.kfb.

    There are four independent rule bases that all do the same thing.  The
    fc_example rule base only uses forward-chaining rules.  The bc_example
    rule base only uses backward-chaining rules.  The bc2_example rule base
    also only uses backward-chaining rules, but with a few optimizations that
    make it run 100 times faster than bc_example.  And the example rule base
    uses all three (though it's a poor use of plans).

    Once the pyke engine is created, all the rule bases loaded and all the
    primary data established as universal facts; there are five functions
    that can be used to run each of the three rule bases: fc_test, bc_test,
    bc2_test, test and general.
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