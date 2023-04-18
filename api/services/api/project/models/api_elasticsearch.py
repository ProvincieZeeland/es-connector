from flask import request, make_response, jsonify
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConflictError
from .api_sharepoint import Api_sharepoint

import os
import json

##############################################################################
#  
#  Api_Elasticsearch
#
#  API for adding, updating and deleting items in our ELasticsearch server
#
#  @author Wim Kosten <w.kosten@zeeland.nl>
#
#  TODO: 
#  - should rewrite using __init__ and use self in the methods. 
#  - exception handling (https://towardsdev.com/goodbye-try-catch-hello-handleexception-effortless-exception-handling-in-python-e6c669a9a5bf)
#
##############################################################################
class Api_Elasticsearch:

    ##############################################################################
    #  
    #  __initElastic
    #
    #  Create Elasticsearch client
    #
    #  @param void
    #  @return (object)Elasticsearch
    #
    ##############################################################################
    def __initElastic():
            
        ELASTIC_HOST     = os.getenv('ES_DB'); 
        ELASTIC_PASSWORD = os.getenv('ES_DB_PW')
        CERT_FINGERPRINT = os.getenv('ES_SHA_FINGERPRINT')

        try:
            return Elasticsearch(ELASTIC_HOST,
                                 ssl_assert_fingerprint=CERT_FINGERPRINT,
                                 basic_auth=("elastic", ELASTIC_PASSWORD))            

        except Exception as err:
            return False


    ##############################################################################
    #  
    #  isAlive
    #
    #  Get info from the Elasticsearch server
    #
    #  @param void
    #  @return json object
    #
    ##############################################################################
    def isAlive(cls):
       
        # https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/connecting.html
        try:
            client = Api_Elasticsearch.__initElastic()

            if (client != False):
                info     = client.info()
                response = {'info': dict(info)}

        except Exception as err:
            raise err
            response = {'name': '', 'version': 0, 'alive': 'NO !'}

        return response
    

    ##############################################################################
    #  
    #  addMetadataToIndex
    #
    #  Add a new document (metadata) to the ES index
    #
    #  @param string indexName
    #  @param string objectID
    #  @param bytes itemData
    #  @return json object
    #
    ##############################################################################
    def addMetadataToIndex(indexName, objectID, itemData):

        # https://elasticsearch-py.readthedocs.io/en/v8.6.2/api.html#module-elasticsearch
        client = Api_Elasticsearch.__initElastic()

        if (client != False):
            try:
                # Add the metadata with the file contents
                added    = client.create(index=indexName, id=objectID, body=itemData)
                response = {'status'      :'ok',
                            'reason'      :'',
                            'http_status' : 200,
                            'response'    : dict(added)}
                return response

            except ConflictError as e:
                response = {'status'      :'error',
                            'reason'      :'Fout tijdens toevoegen van data (conflict error, item bestaat al)',
                            'http_status' : 409}

        else:
            response = {'status'      :'error',
                        'reason'      :'Fout tijdens verbinden met Elasticsearch',
                        'http_status' : 500}

        return response



    ##############################################################################
    #  
    #  updateMetadata
    #
    #  Update an existing document (metadata) 
    #
    #  @param string indexName
    #  @param string objectID
    #  @param bytes itemData
    #  @return json object
    #
    ##############################################################################
    def updateMetadataInIndex(indexName, objectID, itemData):
        
        client = Api_Elasticsearch.__initElastic()

        if (client != False):
            try:
                # Add the metadata with the file contents
                updated  = client.update(index=indexName, id=objectID, doc=itemData)
                response = {'status'      :'ok',
                            'reason'      :'',
                            'http_status' : 200,
                            'response'    : dict(updated)}
                return response

            except:
                response = {'status'      :'error',
                            'reason'      :'Fout bij het updaten van de data',
                            'http_status' : 404}

        else:
            response = {'status'      :'error',
                        'reason'      :'Fout tijdens verbinden met Elasticsearch',
                        'http_status' : 500}

        return response
    

    ##############################################################################
    #  
    #  deleteMetadataFromIndex
    #
    #  Delete an existing document (metadata) 
    #
    #  @param string indexName
    #  @param string objectID
    #  @return json object
    #
    ##############################################################################
    def deleteMetadataFromIndex(indexName, object_id):

        client = Api_Elasticsearch.__initElastic()

        if (client != False):
            try:
                # Add the metadata with the file contents
                deleted  = client.delete(index=indexName, id=object_id)
                response = {'status'      :'ok',
                            'reason'      :'',
                            'http_status' : 200,
                            'response'    : dict(deleted)}
                return response

            except:
                response = {'status'      :'error',
                            'reason'      :'Fout bij verwijderen van de data',
                            'http_status' : 404}

        else:
            response = {'status'      :'error',
                        'reason'      :'Fout tijdens verbinden met Elasticsearch',
                        'http_status' : 500}

        return response
        


    ##############################################################################
    #  
    #  getMetadadaItem
    #
    #  Get a single metadata item using it's index key
    #
    #  @param string indexName
    #  @param string objectID
    #  @return json object
    #
    ##############################################################################
    def getMetadataItem(indexName, object_id):

        client = Api_Elasticsearch.__initElastic()

        if (client != False):
            try:
                # Add the metadata with the file contents
                metadata = client.get(index=indexName, id=object_id)
                response = {"http_status" : 200,
                            "metadata"    : dict(metadata["_source"])}
                
                return response

            except Exception as err:
                response = {"http_status" : 404,
                            "metadata"    : {}}
        else:
            response = {'status'      :'error',
                        'reason'      :'Fout tijdens verbinden met Elasticsearch',
                        'http_status' : 500}

        return response



    ##############################################################################
    #  
    #  zeesterFallback
    #
    #  Remap old ZEESTER id to new object_od
    #
    #  @param string indexName
    #  @param string object_id
    #  @return json object
    #
    # https://kb.objectrocket.com/elasticsearch/how-to-use-the-search-api-for-the-python-elasticsearch-client-265
    #
    ##############################################################################   
    def zeesterFallback(indexName, object_id):

        zeesterSearch = object_id.upper()

        if (zeesterSearch.find("ZEE") != -1):
            zeesterQuery = {"query": 
                                    {
                                     "nested": 
                                     {
                                      "path": "metadata",
                                      "query": 
                                      {
                                       "bool": 
                                       {
                                        "must": [{ "match": { "metadata.zeester_ref": zeesterSearch }}]
                                       }
                                      }
                                     }
                                    }
                           } 
            found        = Api_Elasticsearch.searchMetadata(indexName, zeesterQuery)
            hits         = found["metadata"]["hits"]["hits"]
            counter      = len(hits)

            if (counter > 0):
                response     = {}

                for num, doc in enumerate(hits):
                    response[num] = doc

                hit = response[0]

                if ('_source' in hit):
                    return hit['_source']['object_id']
                
        return False
            

    ##############################################################################
    #  
    #  searchMetadata
    #
    #  Search metadata
    #
    #  @param string indexName
    #  @param string query (JSON)
    #  @return json object
    #
    ##############################################################################
    def searchMetadata(indexName, searchQuery):

        client = Api_Elasticsearch.__initElastic()

        if (client != False):

            try:
                # Add the metadata with the file contents
                results  = client.search(index=indexName, body=searchQuery)
                response = {"http_status" : 200,
                            "query"       : dict(searchQuery),
                            "metadata"    : results}
                
                return response

            except Exception as err:
                raise err
                response = {"http_status" : 500,
                            "metadata"    : {}}
        else:
            response = {'status'      :'error',
                        'reason'      :'Fout tijdens verbinden met Elasticsearch',
                        'http_status' : 500}

        return response    



    