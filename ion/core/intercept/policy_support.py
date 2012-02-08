'''
    This provides the actual invocation of pyke rules processing for the agents
    @author Prashant Kediyal
'''

from __future__ import with_statement
import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)

from ion.core.process.cprocess import Invocation
from ion.core.xacml import request
from ndg.xacml.core.context.result import Decision
from twisted.internet import defer


class PolicySupport():

    """
    Example service interface
    """
    def __init__(self, *args, **kwargs):
        log.info('PolicySupport.__init__()')
        self.pdp = request._createPDP()

    @defer.inlineCallbacks
    def check_policies(self,invocation):

        requestCtx = request._createRequestCtx(invocation)

        if requestCtx is None:
            log.debug('requestCtx is empty')
            invocation.drop(note='Not authorized', code=Invocation.CODE_UNAUTHORIZED)
        else:
            log.debug('request context created')
            response = self.pdp.evaluate(requestCtx)
            log.debug('pdp evaluated response')
            if response is None:
                log.info('response from PDP contains nothing')
                invocation.drop(note='Not authorized', code=Invocation.CODE_UNAUTHORIZED)
            else:
                for result in response.results:
                    if str(result.decision) == Decision.DENY_STR:
                        break
                if str(result.decision) == Decision.DENY_STR:
                    log.info('Policy Interceptor: Returning Not Authorized.')
                    invocation.drop(note='Not authorized', code=Invocation.CODE_UNAUTHORIZED)
                else:
                    log.info('Policy Interceptor: Returning Authorized.')
            log.info('XACML Policy Interceptor permission: '+str(result.decision))
            defer.returnValue(invocation)
        yield (1,)