#!/usr/bin/env python

"""
@file ion/services/coi/identity_registry.py
@authors Roger Unwin, Bill Bollenbacher
@brief service for storing user identities
"""
import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)

from twisted.internet import defer
from ion.core import ioninit, bootstrap

CONF = ioninit.config(__name__)

from ion.core.process.process import Process, ProcessClient, ProcessDesc, ProcessFactory
from ion.core.process.service_process import ServiceProcess, ServiceClient
from ion.core.security.authentication import Authentication
from ion.services.coi.resource_registry_beta.resource_client import ResourceClient, ResourceInstance, ResourceClientError, ResourceInstanceError
from ion.core.exception import ApplicationError

from ion.core.object import object_utils

from ion.core.intercept.policy import subject_has_admin_role, map_ooi_id_to_subject_admin_role, subject_has_dispatcher_queue, map_ooi_id_to_subject_dispatcher_queue, \
 subject_has_data_provider_role, map_ooi_id_to_subject_data_provider_role, subject_has_marine_operator_role, map_ooi_id_to_subject_marine_operator_role

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
   optional string dispatcher_queue=4
   optional string email=5
   optional string life_cycle_state=7;
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
    def is_user_registered(self, user_cert, user_private_key):
        """
        This determines if a user is registered by deriving the subject line from the certificate and scanning the registry for that line.
        It returns True or False
        """
        cont = {
            'user_cert': user_cert,
            'user_private_key': user_private_key,
        }
        
        (content, headers, msg) = yield self.rpc_send('verify_registration', cont)
        log.debug("in is_user_registered client" + str(content))
        defer.returnValue( content )
        

    #
    #
    # UPDATE FIND_USERS when the repository supports this operation
    #
    #

    #--#op_find_users = BaseRegistryService.base_find_resource

    @defer.inlineCallbacks
    def find_users(self, user_description,regex=True,ignore_defaults=True, attnames=None):
        """
        """
        #--if attnames is None: attnames = []
        #--#return self.base_find_resource('find_users',user_description,regex,ignore_defaults,attnames)


    @defer.inlineCallbacks
    def set_identity_lcstate(self, ooi_id, lcstate):
        """
        """
        log.debug("in set_identity_lcstate client")
        
        cont = {
            'ooi_id': ooi_id,
            'lcstate': lcstate
        }

        (content, headers, msg) = yield self.rpc_send('set_lcstate', cont)
        defer.returnValue( content )


    @defer.inlineCallbacks
    def set_identity_lcstate_new(self, ooi_id):
        """
        """
        log.debug("in set_identity_lcstate_new client")
        
        cont = {
            'ooi_id': ooi_id,
            'lcstate': 'New'
        }

        (content, headers, msg) = yield self.rpc_send('set_lcstate', cont)
        defer.returnValue( content )


    @defer.inlineCallbacks
    def set_identity_lcstate_active(self, ooi_id):
        """
        """
        log.debug("in set_identity_lcstate_active client")
        
        cont = {
            'ooi_id': ooi_id,
            'lcstate': 'Active'
        }

        (content, headers, msg) = yield self.rpc_send('set_lcstate', cont)
        defer.returnValue( content )
        

    @defer.inlineCallbacks
    def set_identity_lcstate_inactive(self, ooi_id):
        """
        """
        log.debug("in set_identity_lcstate_inactive client")
        
        cont = {
            'ooi_id': ooi_id,
            'lcstate': 'Inactive'
        }

        (content, headers, msg) = yield self.rpc_send('set_lcstate', cont)
        defer.returnValue( content )


    @defer.inlineCallbacks
    def set_identity_lcstate_decommissioned(self, ooi_id):
        """
        """
        log.debug("in set_identity_lcstate_decommissioned client")
        
        cont = {
            'ooi_id': ooi_id,
            'lcstate': 'Decommissioned'
        }

        (content, headers, msg) = yield self.rpc_send('set_lcstate', cont)
        defer.returnValue( content )


    @defer.inlineCallbacks
    def set_identity_lcstate_retired(self, ooi_id):
        """
        """
        log.debug("in set_identity_lcstate_retired client")
        
        cont = {
            'ooi_id': ooi_id,
            'lcstate': 'Retired'
        }

        (content, headers, msg) = yield self.rpc_send('set_lcstate', cont)
        defer.returnValue( content )


    @defer.inlineCallbacks
    def set_identity_lcstate_developed(self, ooi_id):
        """
        """
        log.debug("in set_identity_lcstate_developed client")
        
        cont = {
            'ooi_id': ooi_id,
            'lcstate': 'Developed'
        }

        (content, headers, msg) = yield self.rpc_send('set_lcstate', cont)
        defer.returnValue( content )


    @defer.inlineCallbacks
    def set_identity_lcstate_commissioned(self, ooi_id):
        """
        """
        log.debug("in set_identity_lcstate_commissioned client")
        
        cont = {
            'ooi_id': ooi_id,
            'lcstate': 'Commissioned'
        }

        (content, headers, msg) = yield self.rpc_send('set_lcstate', cont)
        defer.returnValue( content )
    

class IdentityRegistryException(ApplicationError):
    """
    IdentityRegistryService exception class
    """

class IdentityRegistryService(ServiceProcess):

    # Declaration of service
    declare = ServiceProcess.service_declare(name='identity_service', version='0.1.0', dependencies=[])
    
    def slc_init(self):
        """
        """
        # Service life cycle state. Initialize service here. Can use yields.
        
        # Can be called in __init__ or in slc_init... no yield required
        self.rc = ResourceClient(proc=self)
        #Response = yield self.mc.create_instance(RESOURCE_CFG_RESPONSE_TYPE, MessageName='IR response')
        
        self.instance_counter = 1
        # This is a hack to get past no 
        self._user_dict = {}


    @defer.inlineCallbacks
    def op_set_lcstate(self, request, headers, msg):
        """
        """
        log.debug('in op_get_user')
        identity = yield self.rc.get_instance(request['ooi_id'])

        if request['lcstate'] == 'New':
          identity.ResourceLifeCycleState = identity.NEW
          yield self.rc.put_instance(identity, 'updating LCSTATE to %s' % request['lcstate'])
          yield self.reply_ok(msg, True)
        elif request['lcstate'] == 'Active':
          identity.ResourceLifeCycleState = identity.ACTIVE
          yield self.rc.put_instance(identity, 'updating LCSTATE to %s' % request['lcstate'])
          yield self.reply_ok(msg, True)
        elif request['lcstate'] == 'Inactive':
          identity.ResourceLifeCycleState = identity.INACTIVE
          yield self.rc.put_instance(identity, 'updating LCSTATE to %s' % request['lcstate'])
          yield self.reply_ok(msg, True)
        elif request['lcstate'] == 'Commissioned':
          identity.ResourceLifeCycleState = identity.COMMISSIONED
          yield self.rc.put_instance(identity, 'updating LCSTATE to %s' % request['lcstate'])
          yield self.reply_ok(msg, True)
        elif request['lcstate'] == 'Decommissioned':
          identity.ResourceLifeCycleState = identity.DECOMMISSIONED
          yield self.rc.put_instance(identity, 'updating LCSTATE to %s' % request['lcstate'])
          yield self.reply_ok(msg, True)
        elif request['lcstate'] == 'Retired':
          identity.ResourceLifeCycleState = identity.RETIRED
          yield self.rc.put_instance(identity, 'updating LCSTATE to %s' % request['lcstate'])
          yield self.reply_ok(msg, True)
        elif request['lcstate'] == 'Developed':
          identity.ResourceLifeCycleState = identity.DEVELOPED
          yield self.rc.put_instance(identity, 'updating LCSTATE to %s' % request['lcstate'])
          yield self.reply_ok(msg, True)
        elif request['lcstate'] == 'Update':
          identity.ResourceLifeCycleState = identity.UPDATE
          yield self.rc.put_instance(identity, 'updating LCSTATE to %s' % request['lcstate'])
          yield self.reply_ok(msg, True)
        else:
          yield self.reply_ok(msg, False)


    @defer.inlineCallbacks
    def op_register_user_credentials(self, request, headers, msg):
        """
        This registers a user by storing the user certificate, user private key, and certificate subject line(derived from the certificate)
        It returns a ooi_id which is the uuid of the record and can be used to uniquely identify a user.
        """
        # Check for correct protocol buffer type
        self.CheckRequest(request)
        
        # check for required fields
        if not request.configuration.IsFieldSet('certificate'):
            raise IdentityRegistryException("Required field [certificate] not found in message",
                                            request.ResponseCodes.BAD_REQUEST)
        if not request.configuration.IsFieldSet('rsa_private_key'):
            raise IdentityRegistryException("Required field [rsa_private_key] not found in message",
                                            request.ResponseCodes.BAD_REQUEST)
            
        log.debug('in op_register_user_credentials:\n'+str(request))
        log.debug('in op_register_user_credentials: request.configuration\n'+str(request.configuration))

        response = yield self.register_user_credentials(request)

        yield self.reply_ok(msg, response)

        
    @defer.inlineCallbacks
    def register_user_credentials(self, request):
        log.debug('in register_user_credentials:\n'+str(request))
        identity = yield self.rc.create_instance(IDENTITY_TYPE, ResourceName='Identity Registry', ResourceDescription='User identity information')
        identity.certificate = request.configuration.certificate
        identity.rsa_private_key = request.configuration.rsa_private_key
        
        authentication = Authentication()

        cert_info = authentication.decode_certificate(str(request.configuration.certificate))

        identity.subject = cert_info['subject']
       
        yield self.rc.put_instance(identity, 'Adding identity %s' % identity.subject)
        log.debug('Commit completed, %s' % identity.ResourceIdentity)
        
        # Now we store the subject/ResourceIdentity pair so we can get around not having find.
        self._user_dict[cert_info['subject']] = identity.ResourceIdentity
        # Above line needs to be altered when FIND is implemented

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
        if subject_has_dispatcher_queue(identity.subject):
            map_ooi_id_to_subject_dispatcher_queue(identity.subject, identity.ResourceIdentity)

        # Create the response object...
        Response = yield self.message_client.create_instance(RESOURCE_CFG_RESPONSE_TYPE, MessageName='IR response')
        Response.resource_reference = Response.CreateObject(USER_OOIID_TYPE)
        Response.resource_reference.ooi_id = identity.ResourceIdentity
        Response.result = "OK"
        defer.returnValue(Response)

    @defer.inlineCallbacks
    def op_get_user(self, request, headers, msg):
        """
        This returns user information for a specific ooi_id.
        """
        # Check for correct protocol buffer type
        self.CheckRequest(request)
        
        # check for required fields
        if not request.configuration.IsFieldSet('ooi_id'):
            raise IdentityRegistryException("Required field [ooi_id] not found in message",
                                            request.ResponseCodes.BAD_REQUEST)

        log.debug('in op_get_user:\n'+str(request))
        log.debug('in op_get_user: request.configuration\n'+str(request.configuration))

        response = yield self.get_user(request)
        
        yield self.reply_ok(msg, response)


    @defer.inlineCallbacks
    def get_user(self, request):
        """
        """
        log.debug('in get_user')
        if request.configuration.ooi_id in self._user_dict.values():
            identity = yield self.rc.get_instance(request.configuration.ooi_id)
            # Create the response object...
            Response = yield self.message_client.create_instance(RESOURCE_CFG_RESPONSE_TYPE, MessageName='IR response')
            Response.resource_reference = Response.CreateObject(IDENTITY_TYPE)
            Response.resource_reference.subject = identity.subject
            Response.resource_reference.certificate = identity.certificate
            Response.resource_reference.rsa_private_key = identity.rsa_private_key
            Response.resource_reference.email = identity.email
            if identity.IsFieldSet('profile'):
               i = 0
               for item in identity.profile:
                  log.debug('get_user: setting profile to '+str(item))
                  Response.resource_reference.profile.add()
                  Response.resource_reference.profile[i].name = item.name
                  Response.resource_reference.profile[i].value = item.value
                  i = i + 1
            Response.resource_reference.life_cycle_state = identity.ResourceLifeCycleState
            Response.result = "OK"
            defer.returnValue(Response)
        else:
           log.debug('get_user: no match')
           raise IdentityRegistryException("user [%s] not found"%request.configuration.ooi_id,
                                           request.ResponseCodes.NOT_FOUND)



    @defer.inlineCallbacks
    def op_authenticate_user_credentials(self, request, headers, msg):
        """
        This authenticates that the user exists. If so, the credentials are replaced with the current ones,
        and a ooi_id is returned. If not, None is returned.
        """
        # Check for correct protocol buffer type
        self.CheckRequest(request)
        
        # check for required fields
        if not request.configuration.IsFieldSet('certificate'):
            raise IdentityRegistryException("Required field [certificate] not found in message",
                                            request.ResponseCodes.BAD_REQUEST)
        if not request.configuration.IsFieldSet('rsa_private_key'):
            raise IdentityRegistryException("Required field [rsa_private_key] not found in message",
                                            request.ResponseCodes.BAD_REQUEST)

        log.debug('in op_authenticate_user_credentials:\n'+str(request))
        log.debug('in op_authenticate_user_credentials: request.configuration\n'+str(request.configuration))

        response = yield self.authenticate_user_credentials(request)

        yield self.reply_ok(msg, response)


    @defer.inlineCallbacks
    def authenticate_user_credentials(self, request):
        log.info('in authenticate_user_credentials')

        authentication = Authentication()
        cert_info = authentication.decode_certificate(str(request.configuration.certificate))

        if cert_info['subject'] in self._user_dict.keys():
           log.info('authenticate_user_credentials: Registration VERIFIED')
           identity = yield self.rc.get_instance(self._user_dict[cert_info['subject']])
           identity.certificate = request.configuration.certificate
           identity.rsa_private_key = request.configuration.rsa_private_key
           yield self.rc.put_instance(identity, 'Updated user credentials')
           log.debug(str(identity.ResourceIdentity))
           # Create the response object...
           Response = yield self.message_client.create_instance(RESOURCE_CFG_RESPONSE_TYPE, MessageName='IR response')
           Response.resource_reference = Response.CreateObject(USER_OOIID_TYPE)
           Response.resource_reference.ooi_id = identity.ResourceIdentity
           Response.result = "OK"
           defer.returnValue(Response)
        else:
           log.debug('authenticate_user_credentials: no match')
           raise IdentityRegistryException("user [%s] not found"%cert_info['subject'],
                                           request.ResponseCodes.NOT_FOUND)
  
 
    @defer.inlineCallbacks
    def op_update_user_profile(self, request, headers, msg):
        """
        This updates that the user profile. 
        """
        log.info('in op_update_user_profile')
        
        # Check for correct protocol buffer type
        self.CheckRequest(request)
        
        log.debug('in op_update_user_profile:\n'+str(request))
        log.debug('in op_update_user_profile: request.configuration\n'+str(request.configuration))

        response = yield self.update_user_profile(request)

        yield self.reply_ok(msg, response)
        
        

    @defer.inlineCallbacks
    def update_user_profile(self, request):
        log.info('in update_user_profile')
        
        if request.configuration.subject in self._user_dict.keys():
           log.info('update_user_profile: Found match')
           # first get user's info
           identity = yield self.rc.get_instance(self._user_dict[request.configuration.subject])
           log.info('update_user_profile: identity = '+str(identity))
                       
           if request.configuration.IsFieldSet('email'):
              log.debug('update_user_profile: setting email to %s'%request.configuration.email)
              identity.email = request.configuration.email

           if request.configuration.IsFieldSet('profile'):
              i = 0
              for item in request.configuration.profile:
                  log.debug('update_user_profile: setting profile to '+str(item))
                  identity.profile.add()
                  identity.profile[i].name = item.name
                  identity.profile[i].value = item.value
                  i = i + 1
              
           # now save user's info
           yield self.rc.put_instance(identity, 'Updated user profile information')
           # Create the response object...
           Response = yield self.message_client.create_instance(RESOURCE_CFG_RESPONSE_TYPE, MessageName='IR response')
           Response.result = "OK"
        else:
           log.debug('update_user_profile: no match')
           raise IdentityRegistryException("user [%s] not found"%request.configuration.subject,
                                           request.ResponseCodes.NOT_FOUND)


    @defer.inlineCallbacks
    def op_verify_registration(self, request, headers, msg):
        """
        This determines if a user is registered by deriving the subject line from the certificate and scanning the registry for that line.
        It returns True or False
        """
        log.info('in op_verify_registration')

        authentication = Authentication()
        cert_info = authentication.decode_certificate(request['user_cert'])

        if cert_info['subject'] in self._user_dict.keys():
           log.info('op_verify_registration: Registration VERIFIED')
           yield self.reply_ok(msg, True)
        else:
           yield self.reply_ok(msg, False)
           log.info('op_verify_registration: Registration NOT PRESENT')


    def CheckRequest(self, request):
        # Check for correct request protocol buffer type
        if request.MessageType != RESOURCE_CFG_REQUEST_TYPE:
            raise IdentityRegistryException('Bad message type receieved, ignoring',
                                            request.ResponseCodes.BAD_REQUEST)
        # Check payload in message
        if not request.IsFieldSet('configuration'):
            raise IdentityRegistryException("Required field [configuration] not found in message",
                                            request.ResponseCodes.BAD_REQUEST)
        


# Spawn of the process using the module name
factory = ProcessFactory(IdentityRegistryService)
