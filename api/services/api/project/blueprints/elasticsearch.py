# Import Blueprint / make_response
from flask import Blueprint, make_response, jsonify, request, json, Response, redirect

# Import our decorator used for token validation
from ..models.decorators import validateBearerToken, validateJSON, validateSchema

# Elasticsearch
from elasticsearch import Elasticsearch

# Our models
from ..models.api_elasticsearch import Api_Elasticsearch
from ..models.api_sharepoint import Api_sharepoint
from ..models.api_notify import Api_notify
from ..models.utils import notifyExternalParties, mapJsonToSchema

# Import os for environment stuff
import os

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

    # Get the rawdata used for saving
    rawData  = request.data

    # Set the index
    indexName = os.getenv('ES_INDEXNAME')

    # check if we have an objectid
    if object_id == "":
        response = {"status"    :"failed",
                    "reason"    :"Geen object id bekend",
                    "http_code" : 400}
        return make_response(jsonify(response)), 400     
           
    # Force uppercase
    object_id = object_id.upper()

    # set initial response item
    response = {'object_id'    : object_id, 
                'index_name'   : indexName,
                'content_type' : request.headers.get('Content-Type'),
                'input'        : rawData,
                'last_error'   : "",
                'workflow'     : {'extraction'   : {},
                                  'storage'      : {},
                                  'notification' : {}}
                }
    
    # Map the JSON data to our Elastic schema
    elasticData = mapJsonToSchema(rawData, object_id)
    

    # Do we have a file extension
    if ('FileExtension' not in rawData['Metadata']):
        response['last_error'] = "FileExtension veld bestaat niet"
        return make_response(jsonify(response)), 400
    elif (rawData['Metadata']['FileExtension'] == ""):
        response['last_error'] = "Geen bestandextensie in de metadata (FileExtension veld)"
        return make_response(jsonify(response)), 400


    # Existing file ?
    if (Api_sharepoint.fileExistOnStorage(object_id, rawData['Metadata']['FileExtension']) == False):

        # Hmmm, file not found
        azureFile              = os.getenv('SP_ENDPOINT')+object_id+'.'+rawData['Metadata']['FileExtension'] 
        response['last_error'] = "Content / bestand niet gevonden ("+azureFile+")"
        return make_response(jsonify(response)), 404    


    # Yep, got a file extension. Check if PDF
    if (rawData['Metadata']['FileExtension'] == "pdf"):
            
        # Attempt to extract the text from the PDF
        pdfText                            = Api_sharepoint.extractTextFromExternalPDF(object_id)
        response['workflow']['extraction'] = pdfText

        if (response['workflow']['extraction']['http_status'] != 200):
            response['last_error'] = "Fout bij inlezen tekst uit PDF bestand ("+pdfText["file"]+")"
            return make_response(jsonify(response)), response['workflow']['extraction']['http_status'] 
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
    added                           = Api_Elasticsearch.addMetadataToIndex(indexName, object_id, elasticData)
    response['workflow']['storage'] = added

    # If not http/200 return error status
    if (added['http_status'] != 200):
        response['last_error'] = added['reason']
        return make_response(jsonify(response)), added['http_status']

    # Handle the notifications
    response['workflow']['notification'] = notifyExternalParties('create', object_id) #Api_notify.send('create', object_id)

    # all done, return result
    return make_response(jsonify(response)), 200



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

    # Get the rawdata used for saving
    rawData  = request.data

    # Set the index
    indexName = os.getenv('ES_INDEXNAME')
    
    # check if we have an objectid
    if object_id == "":
        response = {"status"    :"failed",
                    "reason"    :"No object id specified",
                    "http_code" : 400}
        return make_response(jsonify(response)), 400            

    # Force uppercase
    object_id = object_id.upper()

    # set initial response item
    response = {'object_id'    : object_id, 
                'index_name'   : indexName,
                'content_type' : request.headers.get('Content-Type'),
                'input'        : rawData,
                'last_error'   : "",
                'workflow'     : {'extraction'   : {},
                                  'storage'      : {},
                                  'notification' : {}}
                }
    
    # Check if the item exists
    exists = Api_Elasticsearch.getMetadataItem(indexName, object_id)

    if (exists['http_status'] != 200):
        response = {"status"    :"failed",
                    "reason"    :"Item not found",
                    "http_code" : 404}
        return make_response(jsonify(response)), 404
    
    # Map the JSON data to our Elastic schema
    elasticData = mapJsonToSchema(rawData, object_id)
    
    
    # Do we have a file extension
    if ('FileExtension' not in rawData['Metadata']):
        response['last_error'] = "FileExtension veld bestaat niet"
        return make_response(jsonify(response)), 400
    elif (rawData['Metadata']['FileExtension'] == ""):
        response['last_error'] = "Geen bestandextensie in de metadata (FileExtension veld)"
        return make_response(jsonify(response)), 400


    # Existing file ?
    if (Api_sharepoint.fileExistOnStorage(object_id, rawData['Metadata']['FileExtension']) == False):

        # Hmmm, file not found
        azureFile              = os.getenv('SP_ENDPOINT')+object_id+'.'+rawData['Metadata']['FileExtension'] 
        response['last_error'] = "Content / bestand niet gevonden ("+azureFile+")"
        return make_response(jsonify(response)), 404    


    # Yep, got a file extension. Check if PDF
    if (rawData['Metadata']['FileExtension'] == "pdf"):
            
        # Attempt to extract the text from the PDF
        pdfText                            = Api_sharepoint.extractTextFromExternalPDF(object_id)
        response['workflow']['extraction'] = pdfText

        if (response['workflow']['extraction']['http_status'] != 200):
            response['last_error'] = "Fout bij inlezen tekst uit PDF bestand ("+pdfText["file"]+")"
            return make_response(jsonify(response)), response['workflow']['extraction']['http_status'] 
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
    updated                         = Api_Elasticsearch.updateMetadataInIndex(indexName, object_id, elasticData)
    response['workflow']['storage'] = updated

    # If not http/200 return error status
    if (updated['http_status'] != 200):
        return make_response(jsonify(response)), updated['http_status']

    # Handle the notifications
    response['workflow']['notification'] = notifyExternalParties('update', object_id)

    # all done, return result
    return make_response(jsonify(response)), 200



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

    if object_id == "":
        response = {"status"    :"failed",
                    "reason"    :"No object id specified",
                    "http_code" : 400}
        return make_response(jsonify(response)), 400 

    # Set indexname and basic response
    indexName = os.getenv('ES_INDEXNAME')
    response  = {'indexName' : indexName, 
                 'object_id' : object_id,
                 'workflow'  : {'storage'      : {},
                                'notification' : {}}
                }

    # Force uppercase
    object_id = object_id.upper()

    # exec Elastic API call
    response['workflow']['storage'] =  Api_Elasticsearch.deleteMetadataFromIndex(indexName, object_id)

    # check if succesful
    if (response['workflow']['storage']['http_status'] == 200):

        # Handle the notifications
        response['workflow']['notification'] = notifyExternalParties('delete', object_id)

    # all done, return result
    return make_response(jsonify(response)), response['workflow']['storage']['http_status'] 


##############################################################################
#  
#  metadata
#
#  Get a metadata record
#
#  @param string object_id
#  @return 
#
##############################################################################
@bp_elastic.route("/metadata/", methods=['GET'], defaults={'object_id': ''})
@bp_elastic.route("/metadata/<object_id>", methods=['GET'])
#@validateBearerToken
def route_handler_fetch_es_item(object_id):

    if object_id == "":
        response = {"status"    :"failed",
                    "reason"    :"No object id specified",
                    "http_code" : 400}
        return make_response(jsonify(response)), 400 
    
    # set index
    indexName = os.getenv('ES_INDEXNAME')

    # Check for a ZEESTER fallback
    zeesterFallback = Api_Elasticsearch.zeesterFallback(indexName, object_id)

    # If we have a fallback, reassign the object_id
    if (zeesterFallback != False):
        object_id = zeesterFallback

    # Force uppercase
    object_id = object_id.upper()

    # get metadata
    metadata = Api_Elasticsearch.getMetadataItem(indexName, object_id)
    return make_response(jsonify(metadata['metadata'])), metadata['http_status']     



##############################################################################
#  
#  content
#
#  Get a document
#
#  @param string object_id
#  @return 
#
##############################################################################
@bp_elastic.route("/content/", methods=['GET'], defaults={'object_id': ''})
@bp_elastic.route("/content/<object_id>", methods=['GET'])
def route_handler_fetch_document(object_id):

    if object_id == "":
        response = {"status"    :"failed",
                    "reason"    :"No object id specified",
                    "http_code" : 400}
        return make_response(jsonify(response)), 400

    # set index
    indexName = os.getenv('ES_INDEXNAME')

    # Check for a ZEESTER fallback
    zeesterFallback = Api_Elasticsearch.zeesterFallback(indexName, object_id)

    # If we have a fallback, send a http/302 
    if (zeesterFallback != False):
        return redirect("/content/"+zeesterFallback, code=302)

    # No ZEESTER fallback, get metadata to fetch the extension
    metadata = Api_Elasticsearch.getMetadataItem(indexName, object_id)

    # if not http/200 return
    if (metadata['http_status'] != 200):
        return make_response(jsonify({})), metadata['http_status']
    
    # get some metadata properties
    fileExtension = metadata['metadata']["fileextension"]
    mimeType      = metadata['metadata']["mime_type"]

    # get the file
    fileInfo = Api_sharepoint.getFileFromStorage(object_id, fileExtension)

    if (fileInfo["http_status"] != 200):
        return make_response(jsonify({})), fileInfo['http_status']        

    # got the metadata fields and the file contents
    # send headers and content
    fileContent = fileInfo['contents']     

    # send content with correct mimetype
    return Response(fileContent, mimetype=mimeType)
