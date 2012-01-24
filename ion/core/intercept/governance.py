#!/usr/bin/env python

"""
@file ion/core/intercept/policy.py
@author Michael Meisinger
@brief Governance tracking interceptor
"""

from twisted.internet import defer
from zope.interface import implements, Interface
import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)

from ion.core.intercept.interceptor import EnvelopeInterceptor, PassThroughInterceptor
from ion.core.process.cprocess import Invocation


class GovernanceInterceptor(EnvelopeInterceptor):


    def before(self, invocation):

        headers=invocation.content

        if 'receiver-name' in headers:
            log.info('Governance before '+headers['user-id'] + ' ' + headers['receiver-name'])

        if hasattr(invocation.process,'governance_support'):
            log.debug('Governance Interceptor invoked')
            response=invocation.process.governance_support.communicator(invocation.content)
            log.debug('Governance Interceptor received '+str(response))
            if response=='drop':
                invocation.drop(note=response, code=Invocation.CODE_BAD_REQUEST)

        return invocation

    def after(self, invocation):
        headers=invocation.content
        try:
            if 'receiver-name' in headers:
                log.info('Governance before '+headers['user-id'] + ' ' + headers['receiver-name'])
        except Exception as exception:
            pass
        return invocation

#del GovernanceInterceptor
#GovernanceInterceptor = PassThroughInterceptor
