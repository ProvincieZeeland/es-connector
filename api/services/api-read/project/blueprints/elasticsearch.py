# Import Blueprint / make_response
from flask import Blueprint, make_response, jsonify, request, Response, redirect

# Elasticsearch
from elasticsearch import Elasticsearch

# Our models
from ..models.api_elasticsearch_read import Api_Elasticsearch_read
from ..models.api_sharepoint import Api_sharepoint

# Import os/time
import os
import time

# Create blueprint
bp_elastic = Blueprint('elastic', __name__)


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

    # escape object_id ( + - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \ / )
    object_id = Api_Elasticsearch_read.es_sanitize(object_id)

    # Check for a ZEESTER fallback
    zeesterFallback = Api_Elasticsearch_read.zeesterFallback(indexName, object_id)

    # If we have a fallback, reassign the object_id
    if (zeesterFallback != False):
        object_id = zeesterFallback

    # Force uppercase
    object_id = object_id.upper()

    # get metadata
    metadata = Api_Elasticsearch_read.getMetadataItem(indexName, object_id)
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

    # escape object_id ( + - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \ / )
    object_id = Api_Elasticsearch_read.es_sanitize(object_id)

    # Check for a ZEESTER fallback
    zeesterFallback = Api_Elasticsearch_read.zeesterFallback(indexName, object_id)

    # If we have a fallback, send a http/301 
    if (zeesterFallback != False):
        return redirect("/content/"+zeesterFallback, code=301)

    # No ZEESTER fallback, get metadata to fetch the extension
    metadata = Api_Elasticsearch_read.getMetadataItem(indexName, object_id)

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
