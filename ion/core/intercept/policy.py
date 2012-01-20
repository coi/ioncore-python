#!/usr/bin/env python

"""
@file ion/core/intercept/policy.py
@author Prashant Kediyal
@brief Policy checking interceptor
"""

from twisted.internet import defer
from zope.interface import implements, Interface

import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)

from ion.core import ioninit
from ion.core.intercept.interceptor import EnvelopeInterceptor

from ion.core.messaging.message_client import MessageInstance

from ion.core.process.cprocess import Invocation

import time

from ion.util.config import Config

from ion.services.coi.datastore_bootstrap.ion_preload_config \
    import OWNED_BY_ID, HAS_ROLE_ID, ROLE_NAMES_BY_ID, ROLE_IDS_BY_NAME
from ion.services.dm.inventory.association_service import AssociationServiceClient, ASSOCIATION_QUERY_MSG_TYPE
from ion.services.dm.inventory.association_service import IDREF_TYPE
from ion.core.messaging.message_client import MessageClient

from google.protobuf.internal.containers import RepeatedScalarFieldContainer

from ion.core.xacml import request
from ndg.xacml.core.context.result import Decision

CONF = ioninit.config(__name__)
# Master set of roles and their user-friendly names
all_roles = {'ANONYMOUS': 'Guest', 'AUTHENTICATED': 'User', 'DATA_PROVIDER': 'Data Provider',
             'MARINE_OPERATOR': 'Marine Operator', 'EARLY_ADOPTER': 'Early Adopter',
             'OWNER': 'Owner', 'ADMIN': 'Administrator'}

def construct_policy_lists(policydb):
    thedict = {}
    try:
        for policy_entry in policydb:
            role, action, resources = policy_entry
            service, opname = action.split('.', 1)
            assert role in all_roles

            if role == 'ADMIN':
                role_set = set(['ADMIN'])
            elif role == 'OWNER':
                role_set = set(['OWNER', 'ADMIN'])
            elif role == 'MARINE_OPERATOR':
                role_set = set(['MARINE_OPERATOR', 'ADMIN'])
            elif role == 'DATA_PROVIDER':
                role_set = set(['DATA_PROVIDER', 'ADMIN'])
            elif role == 'AUTHENTICATED':
                role_set = set(['AUTHENTICATED', 'ADMIN'])
            else:
                role_set = set(['ANONYMOUS', 'AUTHENTICATED', 'ADMIN'])

            service_dict = thedict.setdefault(service, {})
            op_dict = service_dict.setdefault(opname, {})
            set_of_roles = op_dict.setdefault('roles', set())
            set_of_roles.update(role_set)
            op_dict['resources'] = resources

    except Exception, ex:
        log.exception('----- POLICY INIT ERROR -----')
        raise ex
    return thedict

policydb_filename = ioninit.adjust_dir(CONF.getValue('policydecisionpointdb'))
policy_dictionary = construct_policy_lists(Config(policydb_filename).getObject())

def construct_user_role_lists(userroledict):
    roles = userroledict['roles']

    roledict = {}
    for role_name in ('ADMIN', 'DATA_PROVIDER', 'MARINE_OPERATOR', 'EARLY_ADOPTER'):
        roledict[role_name] = {'subject': set(roles[role_name]), 'ooi_id': set()}

    return roledict

userroledb_filename = ioninit.adjust_dir(CONF.getValue('userroledb'))
role_user_dict = construct_user_role_lists(Config(userroledb_filename).getObject())
user_role_dict = {} # cache the current role for an ooi_id

def subject_has_role(subject, role):
    if role == 'ANONYMOUS':
        return True
    return subject in role_user_dict[role]['subject']

# Role methods
def user_has_role(ooi_id, role):
    if role == 'OWNER':
        # Will be special handled within the policy flow
        return False
    if role == 'ANONYMOUS':
        return True
    elif role == 'AUTHENTICATED':
        return ooi_id != 'ANONYMOUS'
    else:
        return ooi_id in role_user_dict[role]['ooi_id']

def get_current_roles(ooi_id):
    roles = user_role_dict.get(ooi_id, None)
    if roles is None:       return ['AUTHENTICATED']

    # If more than one role, just grab one for now. There should be only one.
    roles -= set(['ANONYMOUS', 'AUTHENTICATED'])
    if len(roles) == 0:     return ['AUTHENTICATED']

    return list(roles)

def map_ooi_id_to_role(ooi_id, role):
    if not role in role_user_dict:
        role_user_dict[role] = {'subject': set(), 'ooi_id': set()}
    role_user_dict[role]['ooi_id'].add(ooi_id)

    if not ooi_id in user_role_dict:
        user_role_dict[ooi_id] = set()
    user_role_dict[ooi_id].add(role)

def unmap_ooi_id_from_role(ooi_id, role):
    if role in role_user_dict:
        if ooi_id in role_user_dict[role]['ooi_id']:
            role_user_dict[role]['ooi_id'].remove(ooi_id)
    if ooi_id in user_role_dict:
        if role in user_role_dict[ooi_id]:
            user_role_dict[ooi_id].remove(role)

def map_ooi_id_to_subject_role(subject, ooi_id, role):
    if subject in role_user_dict[role]['subject']:
        map_ooi_id_to_role(ooi_id, role)

# Role convenience methods
def map_ooi_id_to_subject_admin_role(subject, ooi_id):
    map_ooi_id_to_subject_role(subject, ooi_id, 'ADMIN')
            
def subject_has_admin_role(subject):
    return subject_has_role(subject, 'ADMIN')

def user_has_admin_role(ooi_id):
    return user_has_role(ooi_id, 'ADMIN')

def map_ooi_id_to_subject_data_provider_role(subject, ooi_id):
    map_ooi_id_to_subject_role(subject, ooi_id, 'DATA_PROVIDER')

def subject_has_data_provider_role(subject):
    return subject_has_role(subject, 'DATA_PROVIDER')

def user_has_data_provider_role(ooi_id):
    return user_has_role(ooi_id, 'DATA_PROVIDER')

def map_ooi_id_to_subject_marine_operator_role(subject, ooi_id):
    map_ooi_id_to_subject_role(subject, ooi_id, 'MARINE_OPERATOR')

def subject_has_marine_operator_role(subject):
    return subject_has_role(subject, 'MARINE_OPERATOR')

def user_has_marine_operator_role(ooi_id):
    return user_has_role(ooi_id, 'MARINE_OPERATOR')

def map_ooi_id_to_subject_early_adopter_role(subject, ooi_id):
    map_ooi_id_to_subject_role(subject, ooi_id, 'EARLY_ADOPTER')

def subject_has_early_adopter_role(subject):
    return subject_has_role(subject, 'EARLY_ADOPTER')

def user_has_early_adopter_role(ooi_id):
    return user_has_role(ooi_id, 'EARLY_ADOPTER')

@defer.inlineCallbacks
def load_roles_from_associations(asc):
    role_map = yield asc.get_associations_map({'predicate': HAS_ROLE_ID})
    for user_id, role_id in role_map.iteritems():
        map_ooi_id_to_role(user_id, ROLE_NAMES_BY_ID[role_id])

class PolicyInterceptor(EnvelopeInterceptor):
    def before(self, invocation):
        headers = invocation.content
        return self.is_authorized(headers, invocation)

    def after(self, invocation):
        return invocation

    @defer.inlineCallbacks
    def is_authorized(self, headers, invocation):
        """
        @brief Policy enforcement method which implements the functionality
            conceptualized as the policy decision point (PDP).
        This method
        will take the specified user id, convert it into a role.  A search
        will then be performed on the global policy_dictionary to determine if
        the user has the appropriate authority to access the specified
        resource via the specified action. A final check is made to determine
        if the user's authentication has expired.
        The following rules are applied to determine authority:
        - If there are no policy tuple entries for service, or no policy
        tuple entries for the specified role, the action is assumed to be allowed.
        - Else, there is a policy tuple for this service:operation.  A check
        is made to ensure the user role is equal to or greater than the
        required role.
        Role precedence from lower to higher is:
            ANONYMOUS, AUTHORIZED, OWNER, ADMIN
        @param headers: message content from invocation
        @param invocation: invocation object passed on interceptor stack.
        @return: invocation object indicating status of authority check
        """

        # Ignore messages that are not of performative 'request'
        if headers.get('performative', None) != 'request':
            defer.returnValue(invocation)

        # Reject improperly defined messages
        if not 'user-id' in headers:
            log.error("Policy Interceptor: Rejecting improperly defined message missing user-id [%s]." % str(headers))
            invocation.drop(note='Error: no user-id defined in message header!', code=Invocation.CODE_BAD_REQUEST)
            defer.returnValue(invocation)
        if not 'expiry' in headers:
            log.error("Policy Interceptor: Rejecting improperly defined message missing expiry [%s]." % str(headers))
            invocation.drop(note='Error: no expiry defined in message header!', code=Invocation.CODE_BAD_REQUEST)
            defer.returnValue(invocation)
        if not 'receiver' in headers:
            log.error("Policy Interceptor: Rejecting improperly defined message missing receiver [%s]." % str(headers))
            invocation.drop(note='Error: no receiver defined in message header!', code=Invocation.CODE_BAD_REQUEST)
            defer.returnValue(invocation)
        if not 'op' in headers:
            log.error("Policy Interceptor: Rejecting improperly defined message missing op [%s]." % str(headers))
            invocation.drop(note='Error: no op defined in message header!', code=Invocation.CODE_BAD_REQUEST)
            defer.returnValue(invocation)

        user_id = headers['user-id']
        expirystr = headers['expiry']

        if not type(expirystr) is str:
            log.error("Policy Interceptor: Rejecting improperly defined message with bad expiry [%s]." % str(expirystr))
            invocation.drop(note='Error: expiry improperly defined in message header!', code=Invocation.CODE_BAD_REQUEST)
            defer.returnValue(invocation)

        try:
            expiry = int(expirystr)
        except ValueError, ex:
            log.error("Policy Interceptor: Rejecting improperly defined message with bad expiry [%s]." % str(expirystr))
            invocation.drop(note='Error: expiry improperly defined in message header!', code=Invocation.CODE_BAD_REQUEST)
            defer.returnValue(invocation)

        rcvr = headers['receiver']
        service = rcvr.rsplit('.',1)[-1]

        operation = headers['op']
        log.info('Policy Interceptor: Policy request for service [%s] operation [%s] user_id [%s] expiry [%s]' % (service, operation, user_id, expiry))

        if service in policy_dictionary:
            service_list = policy_dictionary[service]
            # TODO figure out how to handle non-wildcard resource ids
            if operation in service_list:
                role_entry = service_list[operation]['roles']
                log.info('Policy Interceptor: Policy tuple [%s]' % str(role_entry))

                role_match_found = False
                for role in role_entry:
                    if user_has_role(user_id, role):
                        log.info('Policy Interceptor: Role <%s> authentication matches' % role)
                        role_match_found = True
                        break

                if role_match_found == False:
                    # Special handling for ownership role
                    # ANONYMOUS can never own a resource, so return fail
                    if user_id == 'ANONYMOUS':
                        log.warn('Policy Interceptor: Authentication failed for service [%s] operation [%s] resource [%s] user_id [%s] expiry [%s] for roles [%s]. Returning Not Authorized.' % (service, operation, '*', user_id, expiry, str(role_entry)))
                        invocation.drop(note='Not authorized', code=Invocation.CODE_UNAUTHORIZED)
                        defer.returnValue(invocation)

                    isOwnershipPolicy = False
                    for role in role_entry:
                        if role == 'OWNER':
                            isOwnershipPolicy = True
                            break

                    if isOwnershipPolicy == True:
                        return_uuid_list = self.find_uuids(invocation, headers, user_id, service_list[operation]['resources'])
                        if invocation.status != Invocation.STATUS_PROCESS:
                            log.warn('Policy Interceptor: Authentication failed for service [%s] operation [%s] resource [%s] user_id [%s] expiry [%s] for role [OWNER].' % (service, operation, '*', user_id, expiry))
                            defer.returnValue(invocation)
                            
                        yield self.check_owner(user_id, return_uuid_list, invocation)
                        if invocation.status != Invocation.STATUS_PROCESS:
                            log.warn('Policy Interceptor: Authentication failed for service [%s] operation [%s] resource [%s] user_id [%s] expiry [%s] for role [OWNER].' % (service, operation, '*', user_id, expiry))
                            defer.returnValue(invocation)
                        else:
                            log.info('Policy Interceptor: Role <OWNER> authentication matches')
                    else:
                        log.warn('Policy Interceptor: Authentication failed for service [%s] operation [%s] resource [%s] user_id [%s] expiry [%s] for roles [%s]. Returning Not Authorized.' % (service, operation, '*', user_id, expiry, str(role_entry)))
                        invocation.drop(note='Not authorized', code=Invocation.CODE_UNAUTHORIZED)
                        defer.returnValue(invocation)
            else:
                log.info('Policy Interceptor: operation not in policy dictionary.')
        else:
            if (service == 'resource_agent' or service == 'user_agent' or service == 'org_agent'):
                #TODO get all the roles for a user
                #user_roles=[]
                #for role in role_user_dict:
                #    if user_id in role_user_dict[role]['ooi_id']:
                #        user_roles.append(user_id)
                #    derived_data['roles']=user_roles
                #TODO get all the resources in the request
                log.debug('checking XACML policy for message: '+ str(headers))
                #decision={'permit':False}
                yield self.check_policies(invocation)
                defer.returnValue(invocation)

        expiry_time = int(expiry)
        if (expiry_time > 0):
            current_time = time.time()

            if current_time > expiry_time:
                log.warn('Policy Interceptor: Current time [%s] exceeds expiry [%s] for service [%s] operation [%s] resource [%s] user_id [%s] . Returning Not Authorized.' % (str(current_time), expiry, service, operation, '*', user_id))
                invocation.drop(note='Authentication expired', code=Invocation.CODE_UNAUTHORIZED)
                defer.returnValue(invocation)

        log.info('Policy Interceptor: Returning Authorized.')
        defer.returnValue(invocation)

    @defer.inlineCallbacks
    def check_policies(self,invocation):
        requestCtx = request._createRequestCtx(invocation)
        if requestCtx is None:
            log.debug('requestCtx is empty')
            invocation.drop(note='Not authorized', code=Invocation.CODE_UNAUTHORIZED)
        else:
            log.debug('request context created')
            pdp = request._createPDP()
            log.debug('pdp created')
            response = pdp.evaluate(requestCtx)
            log.debug('pdp evaluated response')
            if response is None:
                log.debug('response from PDP contains nothing')
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

    @defer.inlineCallbacks
    def check_owner(self, user_id, uuid_list, invocation):
        self.mc = MessageClient(proc=invocation.process)
        self.asc = AssociationServiceClient(proc=invocation.process)

        for uuid in uuid_list:        
            request = yield self.mc.create_instance(ASSOCIATION_QUERY_MSG_TYPE)

            request.object = request.CreateObject(IDREF_TYPE)
            request.object.key = user_id

            request.predicate = request.CreateObject(IDREF_TYPE)
            request.predicate.key = OWNED_BY_ID

            request.subject = request.CreateObject(IDREF_TYPE)
            request.subject.key = uuid

            # make the request
            log.warn('Calling association service for user id <%s> and uuid <%s>' % (user_id, uuid))
            result = yield self.asc.association_exists(request)
            log.warn('Return from association service call for user id <%s> and uuid <%s>' % (user_id, uuid))
            if result.result == False:
                log.warn('Policy Interceptor: Authentication failed. User <%s> does not own resource <%s>.' % (user_id, uuid))
                invocation.drop(note='Not authorized', code=Invocation.CODE_UNAUTHORIZED)
                return
            else:
                log.warn('Policy Interceptor: User <%s> owns resource <%s>.' % (user_id, uuid))

    def find_uuids(self, invocation, msg, user_id, resources):
        """
        Traverses message structure looking
        for occurrences of field "resource id".
        For each found, association check is made
        to see if user is an owner of the resource.
        """

        log.info('Policy Interceptor: In check_resource_ownership. Resources: <%s>' % str(resources))
        
        content = msg.get('content','')
        if isinstance(content, MessageInstance):
            wrapper = content.Message
            repo = content.Repository
            uuid_list = self.find_uuids_traverse_gpbs(invocation, msg, wrapper, repo, user_id, resources)
            if len(uuid_list) == 0:
                log.error("Policy Interceptor: Rejecting improperly defined message.  No uuids found.")
                invocation.drop(note='Error: Expected uuids missing from message payload!', code=Invocation.CODE_BAD_REQUEST)
            else:
                return uuid_list
        else:
            log.error("Policy Interceptor: Rejecting improperly defined message missing MessageInstance [%s]." % str(msg))
            invocation.drop(note='Error: MessageInstance missing from message payload!', code=Invocation.CODE_BAD_REQUEST)

    def find_uuids_traverse_gpbs(self, invocation, msg, wrapper, repo, user_id, resources, uuid_list = None):
        log.info('Policy Interceptor: In check_resource_ownership_traverse_gpbs')

        if uuid_list is None:
            uuid_list = []

        childLinksSet = wrapper.ChildLinks
        
        if len(childLinksSet) == 0:
            log.info('Policy Interceptor: Returning from check_resource_ownership_traverse_gpbs.  ChildLinksSet zero length.')
            return
            
        for link in wrapper.ChildLinks:
            obj = repo.get_linked_object(link)
            type = obj.ObjectType
            typeId = type.object_id
            log.info('Policy Interceptor: In check_resource_ownership_traverse_gpbs.  Child type: <%s>' % str(typeId))
            if typeId in resources:
                log.info('Policy Interceptor: In check_resource_ownership_traverse_gpbs.  Child type match found in resources')
                gpbMessage = obj.GPBMessage
                uuid = getattr(gpbMessage,resources[typeId])
                log.info('Policy Interceptor: In check_resource_ownership_traverse_gpbs.  GPB type: %s UUID: %s' % (str(typeId),uuid))
                if not uuid:
                    log.error("Policy Interceptor: Rejecting improperly defined message missing expected uuid [%s]." % str(msg))
                    invocation.drop(note='Error: Uuid missing from message payload!', code=Invocation.CODE_BAD_REQUEST)
                    return
                if uuid == '':
                    log.error("Policy Interceptor: Rejecting improperly defined message missing expected uuid [%s]." % str(msg))
                    invocation.drop(note='Error: Uuid missing from message payload!', code=Invocation.CODE_BAD_REQUEST)
                    return
                if isinstance(uuid, RepeatedScalarFieldContainer):
                    uuid_values = uuid._values
                    for id in uuid_values:
                        uuid_list.append(id.decode('utf-8'))
                elif isinstance(uuid, unicode):
                    uuid_list.append(uuid.decode('utf-8'))
                else:
                    log.error("Policy Interceptor: Rejecting improperly defined message with unexpected uuid variable type [%s]." % str(msg))
                    invocation.drop(note='Error: Uuid variable type not supported!', code=Invocation.CODE_BAD_REQUEST)
                    return
                log.info('Policy Interceptor: In check_resource_ownership_traverse_gpbs.  Added UUID: %s to return list' % uuid)

            log.info('Policy Interceptor: Recursing.')
            self.find_uuids_traverse_gpbs(invocation, msg, obj, repo, user_id, resources, uuid_list)
        return uuid_list
                
