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
class Api_Elasticsearch_read:

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

        client = Api_Elasticsearch_read.__initElastic()

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
            zeesterQuery = {"query": {"bool": {"must": [{ "match": { "zeester_ref": object_id}}]}}} 
            found        = Api_Elasticsearch_read.searchMetadata(indexName, zeesterQuery)
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

        client = Api_Elasticsearch_read.__initElastic()

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


    ##############################################################################
    #  
    #  es_sanitize
    #
    #  Sanitize a string to be safe for ES
    #
    #  @param string text
    #  @return string
    #
    ##############################################################################
    def es_sanitize(text):

        # + - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \ /
        escape_table = {"+"  : "",
                        "="  : "",
                        "&&" : "",
                        "||" : "",
                        ">"  : "",
                        "<"  : "",
                        "!"  : "",
                        "{"  : "",
                        "}"  : "",
                        ")"  : "",
                        ")"  : "",
                        "["  : "",
                        "]"  : "",
                        "^"  : "",
                        '"'  : "",
                        "~"  : "",
                        "*"  : "",
                        "?"  : "",
                        ":"  : "",
                        "\\" : "",
                        "/"  : ""
                       }
        return "".join(escape_table.get(c,c) for c in text)
    