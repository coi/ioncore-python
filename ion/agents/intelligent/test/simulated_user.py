#!/usr/bin/env python

"""
@file ion/agent/intelligent/test/simulated_user.py
@author Prashant Kediyal
@brief Invokes test cases on a user_agent and resource_agent
"""

from twisted.internet import defer

from ion.agents.intelligent.user_agent import UserAgentServiceClient
from ion.test.iontest import IonTestCase
import ion.util.ionlog
from ion.core import ioninit


log = ion.util.ionlog.getLogger(__name__)
CONF = ioninit.config(__name__)


class UserTest(IonTestCase):
    """
    Testing example user aagent service.
    """

    @defer.inlineCallbacks
    def setUp(self):
        log.debug('setup')
        yield self._start_container()

    @defer.inlineCallbacks
    def tearDown(self):
        log.debug('teardown')
        yield self._stop_container()


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

