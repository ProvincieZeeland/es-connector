from flask import request
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConflictError

import os
import json
import uuid
import time

##############################################################################
#  
#  Api_Elasticsearch
#
#  API for adding, updating and deleting items in our ELasticsearch server
#
#  @author Wim Kosten <w.kosten@zeeland.nl>
#
##############################################################################
class Api_Elasticsearch:

    # https://www.programiz.com/python-programming/methods/built-in/classmethod
    # https://discuss.elastic.co/t/fleet-elasticsearch-ca-trusted-fingerprint/297200/6

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

        # https://towardsdev.com/goodbye-try-catch-hello-handleexception-effortless-exception-handling-in-python-e6c669a9a5bf
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
    #  addTransactionRecord
    #
    #  Add a transaction record
    #
    #  @param responseData
    #  @return array
    #
    ##############################################################################
    def addTransactionRecord(responseData):

        # Add HTTP headers
        responseData['headers'] = dict(request.headers)

        # Assign vars
        now             = int(time.time() * 1000)
        tid             = uuid.uuid4().hex
        client          = Api_Elasticsearch.__initElastic()
        indexName       = os.getenv("ES_TRANSACTION_INDEXNAME")
        transactionData = {'object_id'          : responseData["object_id"],
                           'transaction_stamp'  : now,
                           'action_requested'   : responseData['action'],
                           'http_response_code' : responseData['http_code'],
                           'transaction_data'   : responseData
                          }

        if (client != False):
            try:
                added    = client.create(index=indexName, id=tid, body=transactionData)
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
