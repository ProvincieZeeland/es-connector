from ..models.utils import readConfigFile
import urllib3
import os

##############################################################################
#  
#  Api_notify
#
#  API for notifying external systems about a change
#
#  @author Wim Kosten <w.kosten@zeeland.nl>
#
##############################################################################
class Api_notify:

    ##############################################################################
    #  
    #  getNotificationEndpoints
    #
    #  Get configured endpoints
    #
    #  @param void
    #  @return json object
    #
    ##############################################################################
    def getNotificationEndpoints():

        try:
            config = readConfigFile()

            if ('es-hub' in config and ('subscribers' in config['es-hub'])):
                subscribers = config['es-hub']['subscribers']
            else:
                subscribers = {}
        except:
            subscribers = {}

        return subscribers            


    ##############################################################################
    #  
    #  send
    #
    #  Send notifications to the configured endpoints
    #
    #  @param string actionm
    #  @param string object_id
    #  @return json object
    #
    ##############################################################################
    def send(action, object_id):

        hubUrl = os.getenv("ES_HUB_HOST")+action+"/"+object_id
        
        try:
            http            = urllib3.PoolManager()
            notifyResponse  = http.request('GET', hubUrl) 
            httpStatus      = notifyResponse.status
            
            if (httpStatus == 200):
                response = {'http_status' : 200,
                            'endpoints'   : Api_notify.getNotificationEndpoints(),
                            'data'        : {}}
            else:
                response = {'http_status' : httpStatus,
                            'endpoints'   : Api_notify.getNotificationEndpoints(),
                            'data'        : {}}

        except Exception as err: 
            response = {'http_status' : 418,
                        'endpoints'   : Api_notify.getNotificationEndpoints(),
                        'data'        : {}}
        return response
