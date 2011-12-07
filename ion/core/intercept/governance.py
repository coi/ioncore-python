#!/usr/bin/env python

"""
@file ion/core/intercept/policy.py
@author Michael Meisinger
@brief Governance tracking interceptor
"""

from twisted.internet import defer
from zope.interface import implements, Interface
#from ion.core.intercept.governance_support import GovernanceSupportServiceClient
import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)

from ion.core import ioninit
from ion.core.intercept.interceptor import EnvelopeInterceptor, PassThroughInterceptor
import ion.util.procutils as pu


class GovernanceInterceptor(EnvelopeInterceptor):
    def before(self, invocation):
        log.debug('Governance Interceptor before method')
        #gsc = GovernanceSupportServiceClient(proc=self)
        #pass the message to the gsc for governance interpretation
        response=gsc.check(invocation.content)
        #print response
        return invocation

    def after(self, invocation):
        log.debug('Governance Interceptor after method')
        return invocation

del GovernanceInterceptor
GovernanceInterceptor = PassThroughInterceptor
