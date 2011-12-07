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
    declare = ServiceProcess.service_declare(name='userone',
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
    def send_request(self, user_id='shenrie', org='ooi', role=['researcher'], resource_id='glider56', op='get_temp',request='service_request'):
        uasc = UserAgentServiceClient(proc=self)
        request_content = {'user_id': user_id, 'org':org, 'role':role, 'resource_id':resource_id,'op':op, 'request':request}
        response = yield uasc.request(request_content)
        log.info(str(response))
        print

    def authorized_user(self, user_id='shenrie', org='ooi', role=['researcher'], resource_id='glider55', op='get_temp',request='service_request'):
        log.debug('authorized_user')
        self.send_request(user_id, org,role,resource_id,op,request)

    def unauthorized_user(self, user_id='shenrie', org='ooi',role=['student'], resource_id='glider55', op='get_temp',request='service_request'):
        log.debug('unauthorized_user')
        self.send_request(user_id, org,role,resource_id,op,request)

    def authorized_user_unauthorized_resource(self, user_id='shenrie', org='ooi', role=['researcher'], resource_id='glider56', op='get_temp',request='service_request'):
        self.send_request(user_id, org,role,resource_id,op,request)


    def enroll(self, user_id='shenrie', org='ooi', role=['researcher'], resource_id = 'SCILAB', op='enrollment_request',request='enroll'):
        log.debug('test enroll')
        #self.send_request(org,role,resource_id,op,request)
        self.send_request(user_id, org,role,resource_id,op,request)

# Spawn of the process using the module name
factory = ProcessFactory(UserOne)

    