#!/usr/bin/env python

"""
@file ion/agent/intelligent/test/user_one.py
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

class UserOne(ServiceProcess):
    """
    Testing example user agent service.
    """
    declare = ServiceProcess.service_declare(name='user_one',
                                             version='0.1.0',
                                             dependencies=[])

    def __init__(self, *args, **kwargs):
        # Service class initializer. Basic config, but no yields allowed.
        ServiceProcess.__init__(self, *args, **kwargs)
        log.info('UserOne.__init__()')

    def slc_init(self):
        # Service life cycle state. Initialize service here. Can use yields.
        pass


    @defer.inlineCallbacks
    def send_request(self, user_id='shenrie', resource_id='glider56', action='get_temp',op='resource_request',content={}):
        uasc = UserAgentServiceClient(proc=self)
        headers={'user-id':user_id, 'content' : {'resource_id':resource_id,'action':action, 'content':content}, 'receiver-name':user_id}
        response  = yield uasc.request(op, headers)
        log.info('response: '+str(response))
        print

    def request_resource(self, token='IPC420', user_id='shenrie', resource_id='glider55', action='get_temp', op='resource_request'):
        log.info('authorized user requests '+ action +' on '+resource_id)
        self.send_request(user_id, resource_id, action, op, {'token':token})


    def enroll(self, user_id='shenrie', resource_id = 'SCILAB', action='enroll', op='org_request'):
        log.info('user requests enroll')
        self.send_request(user_id, resource_id, action, op)

    def list_resources(self, resource_id = 'SCILAB', user_id='shenrie', action='list_resources', op='org_request'):
        log.info('user requests list of resources from ' + resource_id)
        self.send_request(user_id, resource_id, action, op)

    def list_users(self,  resource_id = 'SCILAB', user_id='shenrie', action='list_users', op='org_request'):
        log.info('user requests list of resources from ' + resource_id)
        self.send_request(user_id, resource_id, action, op)

    def validate_token(self, token='IPC420', user_id='shenrie', resource_id = 'SCILAB', action='validate_token', op='org_request'):
        log.info('user requests list of resources from ' + resource_id)
        content={'token':token}
        self.send_request(user_id, resource_id, action,op, content)

    def validate_enrollment(self, user_id='shenrie', resource_id = 'SCILAB',action='validate_enrollment', op='org_request'):
        log.info('user requests list of resources from ' + resource_id)
        self.send_request(user_id, resource_id, action, op)

# Spawn of the process using the module name
factory = ProcessFactory(UserOne)

    