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
    Testing example user aagent service.
    """
    declare = ServiceProcess.service_declare(name='usertwo',
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
    def authorized_user(self,org='ooi', role=['researcher'], resource_id='glider55', op='get_temp'):
        log.debug('test_authorized_user')
        uasc = UserAgentServiceClient(proc=self)
        request_content = {'org':org,'resource_id':resource_id,'op':op, 'role':role}
        response = yield uasc.service_request(request_content)
        print(str(response))
        print

    @defer.inlineCallbacks
    def unauthorized_user(self,org='ooi', role=['student'], resource_id='glider55', op='get_temp'):
        log.debug('test_unauthorized_user')
        uasc = UserAgentServiceClient(proc=self)
        request_content = {'org':org,'resource_id':resource_id,'op':op, 'role':role}
        log.info('request to user agent'+str(request_content))
        response = yield uasc.service_request(request_content)
        log.info(str(response))
        print

    @defer.inlineCallbacks
    def test_authorized_user_unauthorized_resource(self,org='ooi', role=['student'], resource_id='glider56', op='get_temp'):
        log.debug('test_unauthorized_user_unauthorized_resource')
        uasc = UserAgentServiceClient(proc=self)
        request_content = {'org':org,'resource_id':resource_id,'op':op, 'role':role}
        response = yield uasc.service_request(request_content)
        log.info(str(response))
        print

# Spawn of the process using the module name
factory = ProcessFactory(UserTwo)

