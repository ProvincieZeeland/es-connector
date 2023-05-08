import os
from functools import wraps
from .api_token import Api_token
from .utils import readConfigFile 
from flask import jsonify, request, make_response, json
import jsonschema
from jsonschema import validate

from ..models.api_elasticsearch import Api_Elasticsearch
from ..models.utils import API_response, Timing

##############################################################################
#  
#  validateBearerToken
#
#  Decorator function to validate our bearer token
#
#  @param void
#  @return 
#
##############################################################################
def validateBearerToken(f):
   @wraps(f)
   def bearer_decorator(*args, **kwargs):

        # validate the token using our Api_token class
        tokenAuth = Api_token.getTokenFromHeaders(request)

        # if invalid token return error info
        if tokenAuth['http_code'] != 200:
            
            response = {'object_id' : "",
                        'action'    : "validate_bearer_token",
                        'reason'    : tokenAuth['reason'],
                        'http_code' : tokenAuth['http_code']
                       }    

            # Add transaction record
            Api_Elasticsearch.addTransactionRecord(response)
        
            return make_response(jsonify(API_response(tokenAuth))), tokenAuth['http_code']

        # passed, continue with original function / flow
        return f(*args, **kwargs)

   return bearer_decorator
   
   
##############################################################################
#  
#  validateJSON
#
#  Decorator function to validate the posted JSON data
#
#  @param void
#  @return 
#
##############################################################################
def validateJSON(f):
    @wraps(f)
    def input_decorator(*args, **kwargs):

        # Get the raw data (HTTP/POST body)
        try:
            #rawData  = request.data
            rawData = request.get_data(False, False, False)
        
        except Exception as err:

            response = {'object_id' : "",
                        'action'    : "validate_json",
                        'reason'    : "Fout bij inlezen data",
                        'http_code' : 415
                       }    

            # Add transaction record
            Api_Elasticsearch.addTransactionRecord(response)
            return make_response(jsonify(API_response(response))), 415

        # Any content / body received
        if request.content_length == 0:

            response = {'object_id' : "",
                        'action'    : "validate_json",
                        'reason'    : "Content-Length header niet gevonden / data is 0 bytes",
                        'http_code' : 411
                       }    

            # Add transaction record
            Api_Elasticsearch.addTransactionRecord(response)
            return make_response(jsonify(API_response(response))), 415


        # Check if we content-type is JSON (option: json.loads(request.data))
        #if request.headers.get('Content-Type') != "application/json":
        #    response = {"status"    :"failed",
        #                "reason"    :"Incorrect Content-Type, should be application/json",
        #                "http_code" : 418}
        #    return make_response(jsonify(response)), 418
        
        # Attempt to parse as JSON
        try:
            jsonData = json.loads(rawData, strict=False)
        except:

            response = {'object_id' : "",
                        'action'    : "validate_json",
                        'reason'    : "out bij het parsen van de JSON data",
                        'is_json'   : request.is_json,
                        'http_code' : 418
                       }    

            # Add transaction record
            Api_Elasticsearch.addTransactionRecord(response)
            return make_response(jsonify(API_response(response))), 415

        # Fix null values (evil fix)        
        if ('CreatedOn' in jsonData['Metadata']) and (jsonData['Metadata']['CreatedOn'] is None):
            jsonData['Metadata']['CreatedOn'] = ""

        if ('SourceCreatedOn' in jsonData['Metadata']) and (jsonData['Metadata']['SourceCreatedOn'] is None):
            jsonData['Metadata']['SourceCreatedOn'] = ""

        if ('ModifiedOn' in jsonData['Metadata']) and (jsonData['Metadata']['ModifiedOn'] is None):
            jsonData['Metadata']['ModifiedOn'] = ""

        if ('SourceModifiedOn' in jsonData['Metadata']) and (jsonData['Metadata']['SourceModifiedOn'] is None):
            jsonData['Metadata']['SourceModifiedOn'] = ""

        if ('PublicationDate' in jsonData['Metadata']) and (jsonData['Metadata']['PublicationDate'] is None):
            jsonData['Metadata']['PublicationDate'] = ""

        if ('ArchiveDate' in jsonData['Metadata']) and (jsonData['Metadata']['ArchiveDate'] is None):
            jsonData['Metadata']['ArchiveDate'] = ""                        

        # alter the request.data to contain the parsed JSON data
        request.data = jsonData

        # passed, continue with original function / flow
        return f(*args, **kwargs)
    return input_decorator
               

##############################################################################
#  
#  validateSchema
#
#  Decorator function to validate the JSON against our schema
#
#  @param void
#  @return 
#
##############################################################################
def validateSchema(f):
    @wraps(f)
    def schema_decorator(*args, **kwargs):

        config = readConfigFile()

        # schema available
        if ('cdn_schema' not in config):

            response = {'object_id' : "",
                        'action'    : "validate_json_schema",
                        'reason'    : "JSON validatie schema niet gevonden",
                        'http_code' : 500
                       }    

            # Add transaction record
            Api_Elasticsearch.addTransactionRecord(response)
            return make_response(jsonify(API_response(response))), response['http_code']

        # got the schema, let's validate
        try:
            validate(instance=request.data, schema=config['cdn_schema'])

        except jsonschema.exceptions.ValidationError as err:
            
            errorInfo = {"message"   : err.message,
                         "json_path" : err.json_path
                        }

            response = {'object_id' : "",
                        'action'    : "validate_json_schema",
                        'exception' : errorInfo,
                        'reason'    : "JSON data matched niet met schema",
                        'http_code' : 406
                       }    

            # Add transaction record
            Api_Elasticsearch.addTransactionRecord(response)
            return make_response(jsonify(API_response(response))), response['http_code']

        # passed, continue with original function / flow
        return f(*args, **kwargs)

    return schema_decorator
