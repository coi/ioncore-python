#!/usr/bin/env python

"""
@file ion/services/coi/identity_registry.py
@authors Roger Unwin, Bill Bollenbacher
@brief service for storing user identities
"""
import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)
import logging

from twisted.internet import defer
from ion.core import ioninit

CONF = ioninit.config(__name__)

from ion.core.messaging.receiver import FanoutReceiver
from ion.core.process.process import ProcessFactory
from ion.core.process.service_process import ServiceProcess, ServiceClient
from ion.core.exception import ApplicationError
from ion.core.security.authentication import Authentication
from ion.services.coi.resource_registry.resource_client import ResourceClient
from ion.services.dm.inventory.association_service import AssociationServiceClient
from ion.services.coi.resource_registry.association_client import AssociationClient

from ion.core.object import object_utils

from ion.core.intercept.policy import subject_has_admin_role, \
                                      map_ooi_id_to_subject_admin_role, \
                                      subject_has_early_adopter_role, \
                                      map_ooi_id_to_subject_early_adopter_role, \
                                      subject_has_data_provider_role, \
                                      map_ooi_id_to_subject_data_provider_role, \
                                      subject_has_marine_operator_role, \
                                      map_ooi_id_to_subject_marine_operator_role, \
                                      map_ooi_id_to_role, unmap_ooi_id_from_role, \
                                      get_current_roles, all_roles, load_roles_from_associations

from ion.services.coi.datastore_bootstrap.ion_preload_config \
    import IDENTITY_RESOURCE_TYPE_ID, TYPE_OF_ID, HAS_ROLE_ID, ROLE_NAMES_BY_ID, ROLE_IDS_BY_NAME

from ion.services.coi.datastore import ASSOCIATION_TYPE
from ion.core.object.workbench import WorkBenchError
from ion.services.dm.inventory.association_service import PREDICATE_OBJECT_QUERY_TYPE, IDREF_TYPE

PREDICATE_REFERENCE_TYPE = object_utils.create_type_identifier(object_id=25, version=1)

IDENTITY_TYPE = object_utils.create_type_identifier(object_id=1401, version=1)
"""
from ion-object-definitions/net/ooici/services/coi/identity/identity_management.proto
message UserIdentity {
   enum _MessageTypeIdentifier {
       _ID = 1401;
       _VERSION = 1;
   }

   // objects in a protofile are called messages

   optional string subject=1;
   optional string certificate=2;
   optional string rsa_private_key=3;
   optional string name=4;
   optional string institution=5;
   optional string email=6;
   optional string authenticating_organization=7;
   repeated net.ooici.services.coi.identity.NameValuePairType profile=8;
}
"""""

USER_OOIID_TYPE = object_utils.create_type_identifier(object_id=1403, version=1)
"""
message UserOoiId {
   enum _MessageTypeIdentifier {
       _ID = 1403;
       _VERSION = 1;
   }

   // objects in a protofile are called messages

   optional string ooi_id=1;
}
"""

RESOURCE_CFG_REQUEST_TYPE = object_utils.create_type_identifier(object_id=10, version=1)
"""
from ion-object-definitions/net/ooici/core/message/resource_request.proto
message ResourceConfigurationRequest{
    enum _MessageTypeIdentifier {
      _ID = 10;
      _VERSION = 1;
    }
    
    // The identifier for the resource to configure
    optional net.ooici.core.link.CASRef resource_reference = 1;

    // The desired configuration object
    optional net.ooici.core.link.CASRef configuration = 2;
"""

RESOURCE_CFG_RESPONSE_TYPE = object_utils.create_type_identifier(object_id=12, version=1)
"""
from ion-object-definitions/net/ooici/core/message/resource_request.proto
message ResourceConfigurationResponse{
    enum _MessageTypeIdentifier {
      _ID = 12;
      _VERSION = 1;
    }
    
    // The identifier for the resource to configure
    optional net.ooici.core.link.CASRef resource_reference = 1;

    // The desired configuration object
    optional net.ooici.core.link.CASRef configuration = 2;
    
    optional string result = 3;
}
"""

broadcast_name = 'identity_registry_broadcast'

@defer.inlineCallbacks
def get_broadcast_receiver(receive, receive_error):
    bcr = FanoutReceiver(name=broadcast_name, scope=FanoutReceiver.SCOPE_SYSTEM,
                                           handler=receive, error_handler=receive_error)
    bc_name = yield bcr.attach()
    log.info('Listening to identity registry broadcasts: %s' % (bc_name))
    defer.returnValue(bcr)

class IdentityRegistryClient(ServiceClient):
    """
    """
    
    def __init__(self, proc=None, **kwargs):
        """
        """
        if not 'targetname' in kwargs:
            kwargs['targetname'] = "identity_service"
        ServiceClient.__init__(self, proc, **kwargs)


    @defer.inlineCallbacks
    def register_user(self, Identity):
        """
        This registers a user by storing the user certificate, user private key, and certificate subject line(derived from the certificate)
        It returns a ooi_id which is the uuid of the record and can be used to uniquely identify a user.
        """
        log.debug("in register_user client")
        yield self._check_init()       
        (content, headers, msg) = yield self.rpc_send('register_user_credentials', Identity)
        defer.returnValue(content)

        
    @defer.inlineCallbacks
    def update_user_profile(self, Identity):
        log.debug("in update_user_profile client")
        yield self._check_init()       
        (content, headers, msg) = yield self.rpc_send('update_user_profile', Identity)
        defer.returnValue(content)


    @defer.inlineCallbacks
    def get_user(self, Identity):
        log.debug("in get_user client")
        yield self._check_init()       
        (content, headers, msg) = yield self.rpc_send('get_user', Identity)
        defer.returnValue(content)


    @defer.inlineCallbacks
    def authenticate_user(self, Identity):
        """
        This authenticates that the user exists. If so, the credentials are replaced with the current ones, and a ooi_id is returned.
        If not, None is returned.
        """
        log.debug('in authenticate_user client')
        yield self._check_init()       
        (content, headers, msg) = yield self.rpc_send('authenticate_user_credentials', Identity)
        defer.returnValue(content)

        
    @defer.inlineCallbacks
    def get_ooiid_for_user(self, Identity):
        log.debug("in get_ooiid_for_user client")
        yield self._check_init()       
        (content, headers, msg) = yield self.rpc_send('get_ooiid_for_user', Identity)
        defer.returnValue(content)

    @defer.inlineCallbacks
    def set_role(self, user_id, role):
        log.debug("in set_role client")
        yield self._check_init()
        (content, headers, msg) = yield self.rpc_send('set_role', {'user-id': user_id, 'role': role})
        defer.returnValue(content)

    @defer.inlineCallbacks
    def unset_role(self, user_id, role):
        log.debug("in unset_role client")
        yield self._check_init()
        (content, headers, msg) = yield self.rpc_send('unset_role', {'user-id': user_id, 'role': role})
        defer.returnValue(content)

    @defer.inlineCallbacks
    def broadcast(self, msg):
        log.debug('in broadcast for identity registry client')
        yield self._check_init()
        broadcast_target = self.proc.get_scoped_name(FanoutReceiver.SCOPE_SYSTEM, broadcast_name)
        yield self.proc.send(broadcast_target, 'broadcast', msg)

    @defer.inlineCallbacks
    def get_role(self, user_id):
        log.debug("in get_role client")
        yield self._check_init()
        (content, headers, msg) = yield self.rpc_send('get_role', {'user-id': user_id})
        defer.returnValue(content)

class IdentityRegistryException(ApplicationError):
    """
    IdentityRegistryService exception class
    """

class IdentityRegistryService(ServiceProcess):

    # Declaration of service
    declare = ServiceProcess.service_declare(name='identity_service', version='0.1.0', dependencies=[])

    def __init__(self, *args, **kwargs):
        super(IdentityRegistryService, self).__init__(*args, **kwargs)

        self.broadcast_count = 0

    def slc_init(self):
        """
        """
        # Service life cycle state. Initialize service here. Can use yields.

        # Can be called in __init__ or in slc_init... no yield required
        self.rc = ResourceClient(proc=self)
        self.asc = AssociationServiceClient(proc=self)
        self.ac = AssociationClient(proc=self)
        self.irc = IdentityRegistryClient(proc=self)
        #Response = yield self.mc.create_instance(RESOURCE_CFG_RESPONSE_TYPE, MessageName='IR response')

    @defer.inlineCallbacks
    def slc_activate(self):
        # Setup broadcast channel (for policy reloading)
        self.bc_receiver = yield get_broadcast_receiver(self.receive, self.receive_error)

        # Load current role associations
        yield load_roles_from_associations(self.asc)

    @defer.inlineCallbacks
    def op_register_user_credentials(self, request, headers, msg):
        """
        This registers a user by storing the user certificate, user private key, and certificate subject line(derived from the certificate)
        It returns a ooi_id which is the uuid of the record and can be used to uniquely identify a user.
        """
        # Check for correct protocol buffer type
        self._CheckRequest(request)
        
        # check for required fields
        if not request.configuration.IsFieldSet('certificate'):
            raise IdentityRegistryException("Required field [certificate] not found in message",
                                            request.ResponseCodes.BAD_REQUEST)
        if not request.configuration.IsFieldSet('rsa_private_key'):
            raise IdentityRegistryException("Required field [rsa_private_key] not found in message",
                                            request.ResponseCodes.BAD_REQUEST)
            
        if log.getEffectiveLevel() <= logging.DEBUG:
            log.debug('in op_register_user_credentials: request.configuration\n'+str(request.configuration))

        response = yield self.register_user_credentials(request)

        yield self.reply_ok(msg, response)

        
    @defer.inlineCallbacks
    def register_user_credentials(self, request):
        identity = yield self.rc.create_instance(IDENTITY_TYPE, ResourceName='Identity Registry', ResourceDescription='User identity information')
        identity.certificate = request.configuration.certificate
        identity.rsa_private_key = request.configuration.rsa_private_key
        
        authentication = Authentication()

        cert_info = authentication.decode_certificate(str(request.configuration.certificate))

        identity.subject = cert_info['subject']
        log.debug('User subject: <%s> OOI ID: <%s>', identity.subject, identity.ResourceIdentity)

        identity.name = ""
        identity.institution = ""
        identity.email = ""
        identity.authenticating_organization = cert_info['subject_items']['O']
       
        yield self.rc.put_instance(identity, 'Adding identity %s' % identity.subject)
        log.debug('Commit completed, %s' % identity.ResourceIdentity)
        
        # Optionally map OOI ID to subject in admin role dictionary
        if subject_has_admin_role(identity.subject):
            map_ooi_id_to_subject_admin_role(identity.subject, identity.ResourceIdentity)

        # Optionally map OOI ID to subject in data provider role dictionary
        if subject_has_data_provider_role(identity.subject):
            map_ooi_id_to_subject_data_provider_role(identity.subject, identity.ResourceIdentity)

        # Optionally map OOI ID to subject in marine operator role dictionary
        if subject_has_marine_operator_role(identity.subject):
            map_ooi_id_to_subject_marine_operator_role(identity.subject, identity.ResourceIdentity)

        # Optionally map OOI ID to subject in dispatcher queue user dictionary
        if subject_has_early_adopter_role(identity.subject):
            map_ooi_id_to_subject_early_adopter_role(identity.subject, identity.ResourceIdentity)

        # Create the response object...
        Response = yield self.message_client.create_instance(RESOURCE_CFG_RESPONSE_TYPE, MessageName='IR response')
        Response.resource_reference = Response.CreateObject(USER_OOIID_TYPE)
        Response.resource_reference.ooi_id = identity.ResourceIdentity
        Response.result = "OK"
        defer.returnValue(Response)


    @defer.inlineCallbacks
    def op_get_user(self, request, headers, msg):
        """
        This returns user information for a specific ooi_id if the user is registered.
        """
        # Check for correct protocol buffer type
        self._CheckRequest(request)
        
        # check for required fields
        if not request.configuration.IsFieldSet('ooi_id'):
            raise IdentityRegistryException("Required field [ooi_id] not found in message",
                                            request.ResponseCodes.BAD_REQUEST)

        if log.getEffectiveLevel() <= logging.DEBUG:
            log.debug('in op_get_user: request.configuration\n'+str(request.configuration))

        response = yield self.get_user(request)
        
        yield self.reply_ok(msg, response)


    @defer.inlineCallbacks
    def get_user(self, request):
        """
        """
        log.debug('get_user: ooi_id='+str(request.configuration.ooi_id))
        try:
            identity = yield self.rc.get_instance(str(request.configuration.ooi_id))
            # Create the response object...
            Response = yield self.message_client.create_instance(RESOURCE_CFG_RESPONSE_TYPE, MessageName='IR response')
            Response.resource_reference = Response.CreateObject(IDENTITY_TYPE)
            Response.resource_reference.subject = identity.subject
            Response.resource_reference.certificate = identity.certificate
            Response.resource_reference.rsa_private_key = identity.rsa_private_key
            Response.resource_reference.name = identity.name
            Response.resource_reference.institution = identity.institution
            Response.resource_reference.email = identity.email
            Response.resource_reference.authenticating_organization = identity.authenticating_organization
            if identity.IsFieldSet('profile'):
                i = 0
                for item in identity.profile:
                    log.debug('get_user: setting profile to '+str(item))
                    Response.resource_reference.profile.add()
                    Response.resource_reference.profile[i].name = item.name
                    Response.resource_reference.profile[i].value = item.value
                    i = i + 1
            log.debug('get_user: lcs = '+identity._get_life_cycle_state())
            Response.result = "OK"
            defer.returnValue(Response)
        except ApplicationError, ex:
            log.debug('get_user: no match')
            raise IdentityRegistryException("user [%s] not found: %s"%(request.configuration.ooi_id, ex),request.ResponseCodes.NOT_FOUND)


    @defer.inlineCallbacks
    def op_authenticate_user_credentials(self, request, headers, msg):
        """
        This authenticates that the user exists. If so, the credentials are replaced with the current ones,
        and a ooi_id is returned. If not, NOT_FOUND is returned.
        """
        # Check for correct protocol buffer type
        self._CheckRequest(request)
        
        # check for required fields
        if not request.configuration.IsFieldSet('certificate'):
            raise IdentityRegistryException("Required field [certificate] not found in message",
                                            request.ResponseCodes.BAD_REQUEST)
        if not request.configuration.IsFieldSet('rsa_private_key'):
            raise IdentityRegistryException("Required field [rsa_private_key] not found in message",
                                            request.ResponseCodes.BAD_REQUEST)

        if log.getEffectiveLevel() <= logging.DEBUG:
            log.debug('in op_authenticate_user_credentials: request.configuration\n'+str(request.configuration))

        response = yield self.authenticate_user_credentials(request)

        yield self.reply_ok(msg, response)


    @defer.inlineCallbacks
    def authenticate_user_credentials(self, request):
        log.info('in authenticate_user_credentials')

        authentication = Authentication()
        cert_info = authentication.decode_certificate(str(request.configuration.certificate))

        identity, ooi_id = yield self._findUser(cert_info['subject'])
        if identity != None:
           log.info('authenticate_user_credentials: Registration VERIFIED')
           identity.certificate = request.configuration.certificate
           identity.rsa_private_key = request.configuration.rsa_private_key
           yield self.rc.put_instance(identity, 'Updated user credentials')
           log.debug('authenticate_user_credentials: '+str(identity.ResourceIdentity))
           # Create the response object...
           Response = yield self.message_client.create_instance(RESOURCE_CFG_RESPONSE_TYPE, MessageName='IR response')
           Response.resource_reference = Response.CreateObject(USER_OOIID_TYPE)
           Response.resource_reference.ooi_id = identity.ResourceIdentity
           Response.result = "OK"
           defer.returnValue(Response)
        else:
           log.info('authenticate_user_credentials: Certificate Subject not found - maybe a new user.')
           raise IdentityRegistryException("User Certificate Subject [%s] not found - may be a new user" % cert_info['subject'],request.ResponseCodes.NOT_FOUND)
  
 
    @defer.inlineCallbacks
    def op_get_ooiid_for_user(self, request, headers, msg):
        """
        This looks for a user based on a 'subject', and if it finds them an ooi_id is returned. If not, NOT_FOUND is returned.
        """
        # Check for correct protocol buffer type
        self._CheckRequest(request)
        
        # check for required fields
        if not request.configuration.IsFieldSet('subject'):
            raise IdentityRegistryException("Required field [subject] not found in message",request.ResponseCodes.BAD_REQUEST)
 
        if log.getEffectiveLevel() <= logging.DEBUG:
            log.debug('in op_get_ooiid_for_user: request.configuration\n'+str(request.configuration))

        response = yield self.get_ooiid_for_user(request)

        yield self.reply_ok(msg, response)


    @defer.inlineCallbacks
    def get_ooiid_for_user(self, request):
        log.info('in get_ooiid_for_user')

        identity, ooi_id = yield self._findUser(request.configuration.subject)
        if ooi_id != None:
           log.debug('get_ooiid_for_user: ooi_id = '+ooi_id.key)
           # Create the response object...
           Response = yield self.message_client.create_instance(RESOURCE_CFG_RESPONSE_TYPE, MessageName='IR response')
           Response.resource_reference = Response.CreateObject(USER_OOIID_TYPE)
           Response.resource_reference.ooi_id = ooi_id.key
           Response.result = "OK"
           defer.returnValue(Response)
        else:
           log.debug('get_ooiid_for_user: user with subject %s not found'%request.configuration.subject)
           raise IdentityRegistryException("user [%s] not found"%request.configuration.subject,request.ResponseCodes.NOT_FOUND)
  
 
    @defer.inlineCallbacks
    def op_update_user_profile(self, request, headers, msg):
        """
        This updates that the user profile. 
        """
        log.info('in op_update_user_profile')
        
        # Check for correct protocol buffer type
        self._CheckRequest(request)
        
        if log.getEffectiveLevel() <= logging.DEBUG:
            log.debug('in op_update_user_profile: request.configuration\n'+str(request.configuration))

        response = yield self.update_user_profile(request)

        yield self.reply_ok(msg, response)      
        

    @defer.inlineCallbacks
    def update_user_profile(self, request):
        log.info('in update_user_profile')
        
        identity, ooi_id = yield self._findUser(request.configuration.subject)
        if identity != None:
            if log.getEffectiveLevel() <= logging.INFO:
                log.info('update_user_profile: identity = '+str(identity))
                       
            if request.configuration.IsFieldSet('name'):
                log.debug('update_user_profile: setting name to %s'%request.configuration.name)
                identity.name = request.configuration.name
            else:
                log.debug('update_user_profile: name not set')
                       
            if request.configuration.IsFieldSet('institution'):
                log.debug('update_user_profile: setting institution to %s'%request.configuration.institution)
                identity.institution = request.configuration.institution
            else:
                log.debug('update_user_profile: institution not set')
                       
            if request.configuration.IsFieldSet('email'):
                log.debug('update_user_profile: setting email to %s'%request.configuration.email)
                identity.email = request.configuration.email
            else:
                log.debug('update_user_profile: email not set')

            if request.configuration.IsFieldSet('profile'):
                identity.profile.__delslice__(0, identity.profile.__len__())
                i = 0
                for item in request.configuration.profile:
                    log.debug('update_user_profile: setting profile to '+str(item))
                    identity.profile.add()
                    identity.profile[i].name = item.name
                    identity.profile[i].value = item.value
                    i = i + 1
            else:
                log.debug('update_user_profile: profile not set')
              
            # now save user's info
            yield self.rc.put_instance(identity, 'Updated user profile information')
            # Create the response object...
            Response = yield self.message_client.create_instance(RESOURCE_CFG_RESPONSE_TYPE, MessageName='IR response')
            Response.result = "OK"
        else:
            log.debug('update_user_profile: no match')
            raise IdentityRegistryException("user [%s] not found"%request.configuration.subject,request.ResponseCodes.NOT_FOUND)

    @defer.inlineCallbacks
    def create_role_association(self, user_id, role_id):
        association_repo = self.workbench.create_repository(ASSOCIATION_TYPE)

        # Set the subject
        id_ref = association_repo.create_object(IDREF_TYPE)
        id_ref.key = user_id
        association_repo.root_object.subject = id_ref

        # Set the predicate
        id_ref = association_repo.create_object(IDREF_TYPE)
        id_ref.key = HAS_ROLE_ID
        association_repo.root_object.predicate = id_ref

        # Set the Object
        id_ref = association_repo.create_object(IDREF_TYPE)
        id_ref.key = role_id
        association_repo.root_object.object = id_ref

        association_repo.commit('Ownership association created for identity object.')
        yield self.workbench.push('datastore', association_repo)

    @defer.inlineCallbacks
    def _unset_roles(self, user_id, role_id=None):
        ''' Specify a single role_id to remove, else remove all. '''

        request = {'subject': user_id, 'predicate': HAS_ROLE_ID}
        if role_id is not None: request['object'] = role_id
        associations = yield self.asc.get_associations_list(request)
        
        for assoc in associations:
            a_id, a_user_id, role_id = assoc['id'], assoc['user_id'], assoc['role_id']
            role = ROLE_NAMES_BY_ID[role_id]

            # I would do these with DeferredLists, but there should only be one iteration through this loop
            asc_inst = yield self.ac.get_instance(a_id)
            asc_inst.SetNull()
            yield self.rc.put_instance(asc_inst)
            yield self.irc.broadcast({'op': 'unset_user_role', 'user-id': user_id, 'role': role})

    @defer.inlineCallbacks
    def op_set_role(self, content, headers, msg):
        # First remove existing roles
        user_id, roles = content['user-id'], content['role'].replace(' ', '').split(',')
        role_ids = [ROLE_IDS_BY_NAME[role] for role in roles]
        yield self._unset_roles(user_id)

        # Next setup new role association and policy cache
        try:
            for role_id in role_ids:
                yield self.create_role_association(user_id, role_id)
        except WorkBenchError, ex:
            log.error('Failed to create role association: %s' % (ex))
            raise

        for role in roles:
            map_ooi_id_to_role(user_id, role)

            # Tell all the other identity registry services to update the policy cache
            yield self.irc.broadcast({'op': 'set_user_role', 'user-id': user_id, 'role': role})

        response = True
        yield self.reply_ok(msg, response)

    @defer.inlineCallbacks
    def op_unset_role(self, content, headers, msg):
        user_id, roles = content['user-id'], content['role'].replace(' ', '').split(',')
        # First remove locally
        for role in roles:
            unmap_ooi_id_from_role(user_id, role)

        # Broadcast to other containers to remove
        role_ids = [ROLE_IDS_BY_NAME[role] for role in roles]
        for role_id in role_ids:
            yield self._unset_roles(user_id, role_id)

        response = True
        yield self.reply_ok(msg, response)

    @defer.inlineCallbacks
    def op_get_role(self, content, headers, msg):
        """ Get list of roles as a CSV of friendly names """
        user_id = content['user-id']
        roles = ', '.join([all_roles[role] for role in get_current_roles(user_id)])
        response = {'roles': roles}
        yield self.reply_ok(msg, response)

    def op_broadcast(self, content, headers, msg):
        """
        Service operation: communication amongst identity registry containers
        """
        self.broadcast_count += 1
        log.info('op_broadcast(): Received identity registry broadcast #%d' % (self.broadcast_count))

        if 'op' in content:
            op = content['op']
            log.info('doing op_broadcast operation %s' % (op))
            if op == 'set_user_role':
                map_ooi_id_to_role(content['user-id'], content['role'])
            elif op == 'unset_user_role':
                unmap_ooi_id_from_role(content['user-id'], content['role'])

    @defer.inlineCallbacks
    def _findUser(self, Subject):
        """
        Implementation of User find that uses the registry and associations.
        """
        log.debug('_findUser searching for "%s"' %Subject)
        
        # get all the identity resources out of the Association Service
        request = yield self.message_client.create_instance(PREDICATE_OBJECT_QUERY_TYPE)
        pair = request.pairs.add()
   
        # Set the predicate search term
        pref = request.CreateObject(PREDICATE_REFERENCE_TYPE)
        pref.key = TYPE_OF_ID
        pair.predicate = pref
   
        # Set the Object search term
        type_ref = request.CreateObject(IDREF_TYPE)
        type_ref.key = IDENTITY_RESOURCE_TYPE_ID    
        pair.object = type_ref
   
        ooi_id_list = yield self.asc.get_subjects(request)     

        # Now we have a list of ooi_ids. Gotta pull and search them individually.
        for ooi_id in ooi_id_list.idrefs:
            Resource = yield self.rc.get_instance(ooi_id)
            if Subject == getattr(Resource, 'subject'):
                log.debug('subject %s found'%Subject)
                defer.returnValue([Resource, ooi_id])

        log.debug('subject %s not found'%Subject)
        defer.returnValue([None, None])


    def _CheckRequest(self, request):
        # Check for correct request protocol buffer type
        if request.MessageType != RESOURCE_CFG_REQUEST_TYPE:
            raise IdentityRegistryException('Bad message type receieved, ignoring',request.ResponseCodes.BAD_REQUEST)
        # Check payload in message
        if not request.IsFieldSet('configuration'):
            raise IdentityRegistryException("Required field [configuration] not found in message",request.ResponseCodes.BAD_REQUEST)
        
# Spawn of the process using the module name
factory = ProcessFactory(IdentityRegistryService)
