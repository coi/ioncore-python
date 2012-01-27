#!/usr/bin/env python

"""
@file ion/agent/intelligent/test/simulated_user.py
@author Prashant Kediyal
@brief Invokes test cases on a user_agent and resource_agent
"""

from twisted.internet import defer

from ion.agents.intelligent.user_agent import UserAgentServiceClient
from ion.core.process.process import ProcessFactory
from ion.core.process.service_process import ServiceProcess
import ion.util.ionlog
from ion.core import ioninit


log = ion.util.ionlog.getLogger(__name__)
CONF = ioninit.config(__name__)

class UserTwo(ServiceProcess):
    """
    Testing example user agent service.
    """
    declare = ServiceProcess.service_declare(name='user_two',
                                             version='0.1.0',
                                             dependencies=[])

    def __init__(self, *args, **kwargs):
        # Service class initializer. Basic config, but no yields allowed.
        ServiceProcess.__init__(self, *args, **kwargs)
        log.info('UserTwo.__init__()')

    def slc_init(self):
        # Service life cycle state. Initialize service here. Can use yields.
        pass


    @defer.inlineCallbacks
    def send_request(self, user_id='mmeisinger', resource_id = 'SCILAB', action='contribute', op='resource_request', content={'resource_id':'glider56','action':'get_temp'}):
        uasc = UserAgentServiceClient(proc=self)
        headers={'user-id':user_id, 'content' : {'receiver-name':resource_id,'op':action, 'content':content}, 'receiver-name':user_id}
        response  = yield uasc.request(op, headers)
        log.info('response: '+str(response))
        print


    def contribute(self, user_id='mmeisinger', resource_id = 'SCILAB', action='contribute', op='org_request', content={'resource_id':'glider56','action':'get_temp'}):
        log.info('user wishes to contribute '+resource_id)
        self.send_request(user_id, resource_id, action, op, content)

# Spawn of the process using the module name
factory = ProcessFactory(UserTwo)

