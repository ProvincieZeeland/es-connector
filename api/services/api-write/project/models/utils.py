import json
import os
import urllib3
import time
from dateutil.parser import parse
from flask import Blueprint, make_response, jsonify

##############################################################################
#  
#  readConfigFile
#
#  Read the config file
#
#  @param void
#  @return json object
#
##############################################################################
def readConfigFile():
    configFile  = os.getenv('ES_CONFIG')
    fileExists  = os.path.isfile(configFile)

    if fileExists == True:

        try:
            fp = open(configFile, "r") 
            return json.load(fp)
        except:
            return {}
    else:
        return {}
    

##############################################################################
#  
#  notifyExternalParties
#
#  Send notifications to configured endpoints
#
#  @param string action
#  @param string object_id
#  @return json object
#
##############################################################################
def notifyExternalParties(action, object_id):

    hubUrl = os.getenv("ES_HUB_HOST")+action+"/"+object_id
        
    try:
        http            = urllib3.PoolManager()
        notifyResponse  = http.request('GET', hubUrl) 
        httpStatus      = notifyResponse.status
        data            = json.loads(notifyResponse.data)
        
        if (httpStatus == 200):
            response = {'http_status' : 200,
                        'url'         : hubUrl,
                        'data'        : data}
        else:
            response = {'http_status' : httpStatus,
                        'url'         : hubUrl,
                        'data'        : {}}

    except Exception as err: 
        response = {'http_status' : 418,
                    'url'         : hubUrl,
                    'data'        : {}}
    return response


##############################################################################
#  
#  mapJsonToSchema
#
#  Map the received JSON data to our Elastic mapping
#
#  @param object
#  @return object
#
##############################################################################
def mapJsonToSchema(postData, object_id):

    # At this point we have the required fields, create the Elastic schema with 
    # some additional validation / conversion

    mapping                  = {}
    mapping['metadata']      = {}
    mapping['object_id']     = object_id
    mapping['mime_type']     = postData['Metadata']['MimeType']
    mapping['filename']      = postData['Metadata']['FileName']
    mapping['fileextension'] = postData['Metadata']['FileExtension']

    # Field CreatedOn should exist (JSON schema check), parse the date
    if (postData['Metadata']['CreatedOn'] != ""):
        mapping['created'] = parse(postData['Metadata']['CreatedOn'])    

    # Field SourceCreatedOn should exist (JSON schema check), parse the date
    if (postData['Metadata']['SourceCreatedOn'] != ""):
        mapping['source_created'] = parse(postData['Metadata']['SourceCreatedOn'])

    # Field ModifiedOn might be empty
    if ('ModifiedOn' in postData['Metadata']) and (postData['Metadata']['ModifiedOn'] != ""):
        mapping['modified'] = parse(postData['Metadata']['ModifiedOn'])    

    # Field SourceModifiedOn might be empty
    if ('SourceModifiedOn' in postData['Metadata']) and (postData['Metadata']['SourceModifiedOn'] != ""):
        mapping['source_modified'] = parse(postData['Metadata']['SourceModifiedOn'])    

    # Field PublicationDate might be empty
    if ('PublicationDate' in postData['Metadata']['AdditionalMetadata']) and (postData['Metadata']['AdditionalMetadata']['PublicationDate'] != ""):
        mapping['metadata']['publication_date'] = parse(postData['Metadata']['AdditionalMetadata']['PublicationDate'])

    # Field ArchiveDate might be empty
    if ('ArchiveDate' in postData['Metadata']['AdditionalMetadata']) and (postData['Metadata']['AdditionalMetadata']['ArchiveDate'] != ""):
        mapping['metadata']['archive_date'] = parse(postData['Metadata']['AdditionalMetadata']['ArchiveDate'])
    
    # Other required fields (validated in the JSON schema check)
    mapping['metadata']['author']           = postData['Metadata']['AdditionalMetadata']['Author']
    mapping['metadata']['title']            = postData['Metadata']['AdditionalMetadata']['Title']
    mapping['metadata']['document_type']    = postData['Metadata']['AdditionalMetadata']['DocumentType']
    mapping['metadata']['zeester_type']     = postData['Metadata']['AdditionalMetadata']['ZeesterDocumentType']
    mapping['metadata']['zeester_ref']      = postData['Metadata']['AdditionalMetadata']['ZeesterReference']
    mapping['metadata']['retention']        = postData['Metadata']['AdditionalMetadata']['RetentionPeriod']
    mapping['metadata']['classification']   = postData['Metadata']['AdditionalMetadata']['Classification']
    
    return mapping


##############################################################################
#  
#  mapJsonToSchema_v2
#
#  Map the received JSON data to our Elastic mapping version 2
#
#  @param object
#  @return object
#
##############################################################################
def mapJsonToSchema_v2(postData, object_id):

    # At this point we have the required fields, create the Elastic schema with 
    # some additional validation / conversion

    mapping                  = {}
    mapping['object_id']     = object_id

    # Field CreatedOn should exist (JSON schema check), parse the date
    if (postData['Metadata']['CreatedOn'] != ""):
        mapping['created'] = parse(postData['Metadata']['CreatedOn'])    

    # Field ModifiedOn might be empty
    if ('ModifiedOn' in postData['Metadata']) and (postData['Metadata']['ModifiedOn'] != ""):
        mapping['modified'] = parse(postData['Metadata']['ModifiedOn'])    

    # Field SourceCreatedOn should exist (JSON schema check), parse the date
    if (postData['Metadata']['SourceCreatedOn'] != ""):
        mapping['source_created'] = parse(postData['Metadata']['SourceCreatedOn'])

    # Field SourceModifiedOn might be empty
    if ('SourceModifiedOn' in postData['Metadata']) and (postData['Metadata']['SourceModifiedOn'] != ""):
        mapping['source_modified'] = parse(postData['Metadata']['SourceModifiedOn'])    

    # Field PublicationDate might be empty
    if ('PublicationDate' in postData['Metadata']['AdditionalMetadata']) and (postData['Metadata']['AdditionalMetadata']['PublicationDate'] != ""):
        mapping['publication_date'] = parse(postData['Metadata']['AdditionalMetadata']['PublicationDate'])

    # Field ArchiveDate might be empty
    if ('ArchiveDate' in postData['Metadata']['AdditionalMetadata']) and (postData['Metadata']['AdditionalMetadata']['ArchiveDate'] != ""):
        mapping['archive_date'] = parse(postData['Metadata']['AdditionalMetadata']['ArchiveDate'])
    
    # Other required fields (validated in the JSON schema check)
    mapping['mime_type']        = postData['Metadata']['MimeType']
    mapping['filename']         = postData['Metadata']['FileName']
    mapping['fileextension']    = postData['Metadata']['FileExtension']
    mapping['author']           = postData['Metadata']['AdditionalMetadata']['Author']
    mapping['title']            = postData['Metadata']['AdditionalMetadata']['Title']
    mapping['document_type']    = postData['Metadata']['AdditionalMetadata']['DocumentType']
    mapping['zeester_type']     = postData['Metadata']['AdditionalMetadata']['ZeesterDocumentType']
    mapping['zeester_ref']      = postData['Metadata']['AdditionalMetadata']['ZeesterReference']
    mapping['retention']        = postData['Metadata']['AdditionalMetadata']['RetentionPeriod']
    mapping['classification']   = postData['Metadata']['AdditionalMetadata']['Classification']
    
    return mapping


##############################################################################
#  
#  API_response
#
#  When FLASK_DEBUG=0, return a minimal JSON response
#
#  @param object
#  @return object
#
##############################################################################
def API_response(response):

    debugState = os.getenv('ES_FULL_JSON_RESPONSE')
    
    if (debugState == '0'):
        return response
    else:
        newResponse = {}

        return response


##############################################################################
#  
#  timing
#
#  Calculate elapsed time based on passed start (in nanoseconds)
#
#  @param number
#  @return float
#
##############################################################################
def Timing(start):
    
    now     = time.perf_counter_ns()
    elapsed = now-start

    return (elapsed / 1000000000)