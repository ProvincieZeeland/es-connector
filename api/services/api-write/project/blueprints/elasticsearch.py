# Import Blueprint / make_response
from flask import Blueprint, make_response, jsonify, request, Response, redirect #json

# Import our decorator used for token validation
from ..models.decorators import validateBearerToken, validateJSON, validateSchema

# Elasticsearch
#from elasticsearch import Elasticsearch

# Our models
from ..models.api_elasticsearch import Api_Elasticsearch
from ..models.api_sharepoint import Api_sharepoint
#from ..models.api_notify import Api_notify
from ..models.utils import notifyExternalParties, mapJsonToSchema, mapJsonToSchema_v2, API_response, Timing

# Import os/time
import os
import time

# Create blueprint
bp_elastic = Blueprint('elastic', __name__)

##############################################################################
#  
#  create
#
#  Add a new item to the Elasticsearch index
#
#  @param string object_id
#  @return 
#
# Option: get data from XML: https://www.geeksforgeeks.org/python-xml-to-json/
##############################################################################
@bp_elastic.route("/create/", methods=['POST'], defaults={'object_id': ''})
@bp_elastic.route("/create/<object_id>", methods=['POST'])
@validateBearerToken
@validateJSON
@validateSchema
def route_handler_create_es_item(object_id):

    # Start timer
    bp_start = time.perf_counter_ns()     

    # Get the rawdata used for saving
    rawData  = request.data

    # Set the index
    indexName = os.getenv('ES_INDEXNAME')

    # check if we have an objectid
    if object_id == "":
        response = {"status"     :"failed",
                    "reason"     :"Geen object id bekend",
                    "http_code"  : 400,
                    "object_id"  : object_id, 
                    "action"     : 'create',
                    "index_name" : indexName,}
        
        # Add transaction data
        response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
        response['total_time']  = Timing(bp_start)

        return make_response(jsonify(API_response(response))), 400     
           
    # Force uppercase
    object_id = object_id.upper()

    # set initial response item
    response = {'object_id'    : object_id, 
                'action'       : 'create',
                'index_name'   : indexName,
                'content_type' : request.headers.get('Content-Type'),
                'input'        : rawData,
                'http_code'    : 0,
                'last_error'   : "",
                "timing"       : {'extraction'   : 0,
                                  'storage'      : 0,
                                  'notification' : 0},
                'workflow'     : {'extraction'   : {},
                                  'storage'      : {},
                                  'notification' : {}}
                }
    
    # Map the JSON data to our Elastic schema
    #elasticData = mapJsonToSchema(rawData, object_id)
    elasticData = mapJsonToSchema_v2(rawData, object_id)
    
    # Do we have a file extension
    if ('FileExtension' not in rawData['Metadata']):
        response['last_error'] = "FileExtension veld bestaat niet"
        response['http_code']  = 400

        # Add transaction data
        response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
        response['total_time']  = Timing(bp_start)

        return make_response(jsonify(API_response(response))), 400
    
    elif (rawData['Metadata']['FileExtension'] == ""):
        response['last_error'] = "Geen bestandextensie in de metadata (FileExtension veld)"
        response['http_code']  = 400

        # Add transaction data
        response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
        response['total_time']  = Timing(bp_start)

        return make_response(jsonify(API_response(response))), 400


    # Existing file ?
    sp_start = time.perf_counter_ns()

    if (Api_sharepoint.fileExistOnStorage(object_id, rawData['Metadata']['FileExtension']) == False):

        # Hmmm, file not found
        azureFile              = os.getenv('SP_ENDPOINT')+object_id+'.'+rawData['Metadata']['FileExtension'] 
        response['last_error'] = "Content / bestand niet gevonden ("+azureFile+")"
        response['http_code']  = 404

        # Add transaction data
        response['timing']['extraction'] = Timing(sp_start)
        response['transaction']          = Api_Elasticsearch.addTransactionRecord(response)
        response['total_time']           = Timing(bp_start)
        
        return make_response(jsonify(API_response(response))), 404    


    # Yep, got a file extension. Check if PDF
    if (rawData['Metadata']['FileExtension'] == "pdf"):
            
        # Attempt to extract the text from the PDF
        pdfText                            = Api_sharepoint.extractTextFromExternalPDF(object_id)
        response['workflow']['extraction'] = pdfText
        response['timing']['extraction']   = Timing(sp_start)

        if (response['workflow']['extraction']['http_status'] != 200):
            response['last_error'] = "Fout bij inlezen tekst uit PDF bestand ("+pdfText["file"]+")"
            response['http_code']  = response['workflow']['extraction']['http_status'] 
            
            # Add transaction data
            response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
            response['total_time']  = Timing(bp_start)

            return make_response(jsonify(API_response(response))), response['workflow']['extraction']['http_status'] 
        else:
            # Add the extracted text and some metadata to our received JSON data
            elasticData["content"]           = pdfText["body"]
            elasticData["document_metadata"] = {"pages" : pdfText["pages"],
                                                "size"  : pdfText["size"],
                                                "meta"  : pdfText["metadata"]}
    else:
        elasticData["content"]           = ""
        elasticData["document_metadata"] = {}                 


    # Attempt to add metadata
    es_start                        = time.perf_counter_ns()
    added                           = Api_Elasticsearch.addMetadataToIndex(indexName, object_id, elasticData)
    response['http_code']           = added['http_status']
    response['workflow']['storage'] = added
    response['timing']['storage']   = Timing(es_start)

    # If not http/200 return error status
    if (added['http_status'] != 200):
        response['last_error'] = added['reason']
        response['http_code']  = added['http_status']

        # Add transaction data
        response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
        response['total_time']  = Timing(bp_start)

        return make_response(jsonify(API_response(response))), added['http_status']

    # Handle the notifications
    hub_start                            = time.perf_counter_ns()
    response['workflow']['notification'] = notifyExternalParties('create', object_id) #Api_notify.send('create', object_id)
    response['timing']['notification']   = Timing(hub_start)

    # all done, return result
    # Add transaction data
    response['http_code']   = 200
    response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
    response['total_time']  = Timing(bp_start)

    return make_response(jsonify(API_response(response))), 200



##############################################################################
#  
#  update
#
#  Update an existing item
#
#  @param string object_id
#  @return 
#
##############################################################################
@bp_elastic.route("/update/", methods=['POST'], defaults={'object_id': ''})
@bp_elastic.route("/update/<object_id>", methods=['POST'])
@validateBearerToken
@validateJSON
@validateSchema
def route_handler_update_es_item(object_id):

    # Start timer
    bp_start = time.perf_counter_ns() 

    # Get the rawdata used for saving
    rawData  = request.data

    # Set the index
    indexName = os.getenv('ES_INDEXNAME')
    
    # check if we have an objectid
    if object_id == "":
        response = {"status"     :"failed",
                    "reason"     :"Geen object id bekend",
                    "http_code"  : 400,
                    "object_id"  : object_id, 
                    "action"     : 'create',
                    "index_name" : indexName}
        
        # Add transaction data
        response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
        response['total_time']  = Timing(bp_start)

        return make_response(jsonify(API_response(response))), 400            

    # Force uppercase
    object_id = object_id.upper()

    # set initial response item
    # set initial response item
    response = {'object_id'    : object_id, 
                'action'       : 'update',
                'index_name'   : indexName,
                'content_type' : request.headers.get('Content-Type'),
                'input'        : rawData,
                'http_code'    : 0,
                'last_error'   : "",
                "timing"       : {'get_metadata' : 0, 
                                  'extraction'   : 0,
                                  'storage'      : 0,
                                  'notification' : 0},
                'workflow'     : {'extraction'   : {},
                                  'storage'      : {},
                                  'notification' : {}}
                }
    
    # Check if the item exists
    meta_start                         = time.perf_counter_ns()
    exists                             = Api_Elasticsearch.getMetadataItem(indexName, object_id)
    response['timing']['get_metadata'] = Timing(meta_start)

    if (exists['http_status'] != 200):
        response['last_error'] = "Item bestaat niet"
        response['http_code']  = 400
        
        # Add transaction data
        response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
        response['total_time']  = Timing(bp_start)

        return make_response(jsonify(API_response(response))), 404
    
    # Map the JSON data to our Elastic schema
    elasticData = mapJsonToSchema_v2(rawData, object_id)
    
    # Do we have a file extension
    if ('FileExtension' not in rawData['Metadata']):
        response['last_error'] = "FileExtension veld bestaat niet"
        response['http_code']  = 400

        # Add transaction data
        response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
        response['total_time']  = Timing(bp_start)

        return make_response(jsonify(API_response(response))), 400
    
    elif (rawData['Metadata']['FileExtension'] == ""):
        response['last_error'] = "Geen bestandextensie in de metadata (FileExtension veld)"
        response['http_code']  = 400

        # Add transaction data
        response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
        response['total_time']  = Timing(bp_start)

        return make_response(jsonify(API_response(response))), 400


    # Existing file ?
    sp_start = time.perf_counter_ns()

    if (Api_sharepoint.fileExistOnStorage(object_id, rawData['Metadata']['FileExtension']) == False):

        # Hmmm, file not found
        azureFile              = os.getenv('SP_ENDPOINT')+object_id+'.'+rawData['Metadata']['FileExtension'] 
        response['last_error'] = "Content / bestand niet gevonden ("+azureFile+")"
        response['http_code']  = 404

        # Add transaction data
        response['timing']['extraction'] = Timing(sp_start)
        response['transaction']          = Api_Elasticsearch.addTransactionRecord(response)
        response['total_time']           = Timing(bp_start)

        return make_response(jsonify(API_response(response))), 404    


    # Yep, got a file extension. Check if PDF
    if (rawData['Metadata']['FileExtension'] == "pdf"):
            
        # Attempt to extract the text from the PDF
        pdfText                            = Api_sharepoint.extractTextFromExternalPDF(object_id)
        response['workflow']['extraction'] = pdfText
        response['timing']['extraction']   = Timing(sp_start)

        if (response['workflow']['extraction']['http_status'] != 200):
            response['last_error'] = "Fout bij inlezen tekst uit PDF bestand ("+pdfText["file"]+")"
            response['http_code']  = response['workflow']['extraction']['http_status']
            
            # Add transaction data
            response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
            response['total_time']  = Timing(bp_start)

            return make_response(jsonify(API_response(response))), response['workflow']['extraction']['http_status'] 
        else:
            # Add the extracted text and some metadata to our received JSON data
            elasticData["content"]           = pdfText["body"]
            elasticData["document_metadata"] = {"pages" : pdfText["pages"],
                                                "size"  : pdfText["size"],
                                                "meta"  : pdfText["metadata"]}
    else:
        elasticData["content"]           = ""
        elasticData["document_metadata"] = {}   

    # Attempt to add metadata
    es_start                        = time.perf_counter_ns()
    updated                         = Api_Elasticsearch.updateMetadataInIndex(indexName, object_id, elasticData)
    response['workflow']['storage'] = updated
    response['timing']['storage']   = Timing(es_start)

    # If not http/200 return error status
    if (updated['http_status'] != 200):
        response['http_code']  = updated['http_status']
        
        # Add transaction data
        response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
        response['total_time']  = Timing(bp_start)

        return make_response(jsonify(API_response(response))), updated['http_status']

    # Handle the notifications
    hub_start                            = time.perf_counter_ns()
    response['workflow']['notification'] = notifyExternalParties('update', object_id)
    response['timing']['notification']   = Timing(hub_start)

    # all done, return result
    response['http_code']   = 200
    response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
    response['total_time']  = Timing(bp_start)

    return make_response(jsonify(API_response(response))), 200



##############################################################################
#  
#  delete
#
#  Delete an item from the Elasticsearch index
#
#  @param string object_id
#  @return 
#
##############################################################################
@bp_elastic.route("/delete/", methods=['POST'], defaults={'object_id': ''})
@bp_elastic.route("/delete/<object_id>", methods=['DELETE', 'GET'])
@validateBearerToken
def route_handler_delete_es_item(object_id):

    # Start timer
    bp_start = time.perf_counter_ns() 

    if object_id == "":
        response = {"status"     :"failed",
                    "reason"     :"Geen object id bekend",
                    "http_code"  : 400,
                    "object_id"  : object_id, 
                    "action"     : 'delete',
                    "index_name" : indexName}
        
        # all done, return result
        response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
        response['total_time']  = Timing(bp_start)

        return make_response(jsonify(API_response(response))), 400 

    # Set indexname and basic response
    indexName = os.getenv('ES_INDEXNAME')
    response = {'object_id'    : object_id, 
                'action'       : 'delete',
                'index_name'   : indexName,
                'content_type' : request.headers.get('Content-Type'),
                'http_code'    : 0,
                'last_error'   : "",
                'timing'       : {'storage'      : 0,
                                  'notification' : 0},
                'workflow'     : {'storage'      : {},
                                  'notification' : {}}
                }

    # Force uppercase
    object_id = object_id.upper()

    # exec Elastic API call
    del_start                       = time.perf_counter_ns()
    response['workflow']['storage'] =  Api_Elasticsearch.deleteMetadataFromIndex(indexName, object_id)
    response['timing']['storage']   = Timing(del_start)

    # If not http/200 return error status
    if (response['workflow']['storage']['http_status'] != 200):
        response['http_code'] = response['workflow']['storage']['http_status']
        
        # Add transaction data
        response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
        response['total_time']  = Timing(bp_start)
        
        return make_response(jsonify(API_response(response))), response['workflow']['storage']['http_status']

    # Handle the notifications
    hub_start                            = time.perf_counter_ns()
    response['workflow']['notification'] = notifyExternalParties('delete', object_id)
    response['timing']['notification']   = Timing(hub_start)

    # all done, return result
    response['http_code']   = 200
    response['transaction'] = Api_Elasticsearch.addTransactionRecord(response)
    response['total_time']  = Timing(bp_start)

    # all done, return result
    return make_response(jsonify(API_response(response))), 200 

