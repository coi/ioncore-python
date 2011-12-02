#!/usr/bin/env python

"""
@file ion/core/xacml/support.py
@author Prashant Kediyal
@brief Provides helper functions
"""
from os import path

from ndg.xacml.parsers.etree.factory import ReaderFactory

from ndg.xacml.core import Identifiers
from ndg.xacml.core.attribute import Attribute
from ndg.xacml.core.attributevalue import (AttributeValue,
                                           AttributeValueClassFactory)

from ndg.xacml.core.context.request import Request
from ndg.xacml.core.context.subject import Subject
from ndg.xacml.core.context.resource import Resource
from ndg.xacml.core.context.action import Action
from ndg.xacml.core.context.pdp import PDP

import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)

from ion.core import ioninit
CONF = ioninit.config(__name__)

policydb_filename = ioninit.adjust_dir(CONF.getValue('policydecisionpointdb')) 

THIS_DIR = path.dirname(__file__)
XACML_ION_POLICY_FILENAME='ion_agent_policies.xml'
XACML_POLICY_FILEPATH=path.join(THIS_DIR, XACML_ION_POLICY_FILENAME)

SERVICE_PROVIDER_ATTRIBUTE_ID="urn:oasis:names:tc:xacml:1.0:ooici:resource:service-provider"
ROLE_ATTRIBUTE_ID='urn:oasis:names:tc:xacml:1.0:ooici:subject-id-role'
#"""XACML DATATYPES"""
attributeValueFactory = AttributeValueClassFactory()
AnyUriAttributeValue = attributeValueFactory(AttributeValue.ANY_TYPE_URI)
StringAttributeValue = attributeValueFactory(AttributeValue.STRING_TYPE_URI)



def _createPDP():
        """Create PDP from ion agents policy file"""
        pdp = PDP.fromPolicySource(XACML_POLICY_FILEPATH, ReaderFactory)
        return pdp

def _createRequestCtx(msg):
    print 'role ' + str(msg['content']['role'])
    if msg['content']['role'] is None:
        log.warn('empty request created')
        print 'no role'
        return

    subject_id=msg['user-id']
    org=msg['content']['org']
    subjectRoles=msg['content']['role']
    resource_id=msg['content']['resource_id']
    action_id=msg['content']['op']

    print subject_id + " - " + org + " - "+ str(subjectRoles)+" - "+resource_id+" - "+action_id
    #agent_id=msg['receiver'].split(".")[1]
    #subject_id_qualifier=agent
    #agent_type = msg['receiver'].rsplit('.',1)[-1]

    
    #    """Create empty request"""
    request = Request()

    #
    # create subject and populate it with appropriate data
    #
    subject = Subject()
    log.debug('empty subject created')
        # create subject id attribute and populate it with appropriate data
    subjectIdAttribute = Attribute()
    log.debug('empty subject attribute created')
    subjectIdAttribute.attributeId = Identifiers.Subject.SUBJECT_ID
    subjectIdAttribute.dataType = StringAttributeValue.IDENTIFIER
    subjectIdAttribute.attributeValues.append(StringAttributeValue())
    subjectIdAttribute.attributeValues[-1].value = subject_id
    log.debug('added data and type to subject attribute')
        # create subject qualifier attribute and populate it with appropriate data
    subjectQualifierAttribute = Attribute()
    log.debug('empty attribute created')
    subjectQualifierAttribute.attributeId = Identifiers.Subject.SUBJECT_ID_QUALIFIER
    subjectQualifierAttribute.dataType = StringAttributeValue.IDENTIFIER
    subjectQualifierAttribute.attributeValues.append(StringAttributeValue())
    subjectQualifierAttribute.attributeValues[-1].value = org
    log.debug('added data and type to subject qualifier attribute')

# create role attribute for the subject's, possibly, multiple roles
    for role in subjectRoles:
        roleAttribute = Attribute()
        roleAttribute.attributeId = ROLE_ATTRIBUTE_ID
        roleAttribute.dataType = StringAttributeValue.IDENTIFIER
        roleAttribute.attributeValues.append(StringAttributeValue())
        roleAttribute.attributeValues[-1].value = role
        

        # add attributes to the subject element
    subject.attributes.append(subjectIdAttribute)
    subject.attributes.append(subjectQualifierAttribute)
    subject.attributes.append(roleAttribute)

        # add the subject element to the request
    request.subjects.append(subject)

    # create the resource element
    resource = Resource()
    # create the resource attribute
    resourceAttribute = Attribute()
    resourceAttribute.attributeId = Identifiers.Resource.RESOURCE_ID
    resourceAttribute.dataType = StringAttributeValue.IDENTIFIER
    resourceAttribute.attributeValues.append(StringAttributeValue())
    resourceAttribute.attributeValues[-1].value = resource_id
    # add attributes to the resource element
    resource.attributes.append(resourceAttribute)
    # add the resource element to the request
    request.resources.append(resource)

    # create the resource element
    #resource = Resource()
    # create the resource attribute
    #resourceAttribute = Attribute()
    #resourceAttribute.attributeId = SERVICE_PROVIDER_ATTRIBUTE
    #resourceAttribute.dataType = StringAttributeValue.IDENTIFIER
    #resourceAttribute.attributeValues.append(StringAttributeValue())
    #resourceAttribute.attributeValues[-1].value = resource_service_id
    # add attributes to the resource element
    #resource.attributes.append(resourceAttribute)
    # add the resource element to the request
    #request.resources.append(resource)


    # create the action element
    request.action = Action()
    # create the action attribute
    actionAttribute = Attribute()
    actionAttribute.attributeId = Identifiers.Action.ACTION_ID
    actionAttribute.dataType = StringAttributeValue.IDENTIFIER
    actionAttribute.attributeValues.append(StringAttributeValue())
    actionAttribute.attributeValues[-1].value = action_id
    # add attributes to the action element
    request.action.attributes.append(actionAttribute)
    return request
  