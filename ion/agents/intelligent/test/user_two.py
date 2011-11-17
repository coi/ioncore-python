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
    def test_authorized_user(self):
        log.debug('test_authorized_user')
        services = [
            {'name':'useragent','module':'ion.agents.intelligent.user_agent','class':'UserAgentService'},
            {'name':'resourceagent','module':'ion.agents.intelligent.resource_agent','class':'ResourceAgentService'},
        ]

        sup = yield self._spawn_processes(services)
        #Uncomment the following line when using the eclipse debug server
        #pydevd.settrace()
        uasc = UserAgentServiceClient(proc=sup)
        request_content = {'org':'ooi','resource_id':'glider55','op':'get_temp'}
        permit_decision = yield uasc.service_request(request_content)
        log.info(str(permit_decision))
        print
        print

    @defer.inlineCallbacks
    def test_unauthorized_user(self):
        log.debug('test_unauthorized_user')
        services = [
            {'name':'useragent','module':'ion.agents.intelligent.user_agent','class':'UserAgentService'},
            {'name':'resourceagent','module':'ion.agents.intelligent.resource_agent','class':'ResourceAgentService'},
        ]

        sup = yield self._spawn_processes(services)

        #Uncomment the following line when using the eclipse debug server
        #pydevd.settrace()
        uasc = UserAgentServiceClient(proc=sup)
        request_content = {'org':'nooi','resource_id':'glider55','op':'get_temp'}
        log.info('request to user agent'+str(request_content))
        permit_decision = yield uasc.service_request(request_content)
        log.info(str(permit_decision))
        print
        print

    @defer.inlineCallbacks
    def test_authorized_user_unauthorized_resource(self):
        log.debug('test_unauthorized_user_unauthorized_resource')
        services = [
            {'name':'useragent','module':'ion.agents.intelligent.user_agent','class':'UserAgentService'},
            {'name':'resourceagent','module':'ion.agents.intelligent.resource_agent','class':'ResourceAgentService'},
        ]

        sup = yield self._spawn_processes(services)

        #Uncomment the following line when using the eclipse debug server
        #pydevd.settrace()
        uasc = UserAgentServiceClient(proc=sup)
        request_content = {'org':'ooi','resource_id':'glider56','op':'get_temp'}
        permit_decision = yield uasc.service_request(request_content)
        log.info(str(permit_decision))
        print
        print

# Spawn of the process using the module name
factory = ProcessFactory(UserTwo)

