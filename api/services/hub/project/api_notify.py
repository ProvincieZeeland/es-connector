import urllib3
import os
from flask import json

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
            config = Api_notify.readConfigFile()

            if ('es-hub' in config and ('subscribers' in config['es-hub'])):
                subscribers = config['es-hub']['subscribers']
            else:
                subscribers = {}
        except:
            subscribers = {}

        return subscribers            


    ##############################################################################
    #  
    #  dispatch
    #
    #  Send notifications to the configured endpoints
    #
    #  @param string actionm
    #  @param string object_id
    #  @param object settings
    #  @return json object
    #
    ##############################################################################
    def dispatch(action, object_id, settings):

        # settings =>
        #
        # "description"   : "Mock notifier",
        # "endpoint"      : "http//notify-mock:5003/notify/",
        # "method"        : "get",
        # "auth"          : {}

        # Set nofity url, for now we always add action and object_id even if POST method
        notifyUrl = settings['endpoint']+action+"/"+object_id

        # set basic response
        response = {"action"        : action,
                    "object_id"     : object_id,
                    "settings"      : settings,
                    "url"           : notifyUrl,
                    "http_response" : 0}

        # attempt to call the endpoint        
        try:
            http                      = urllib3.PoolManager()
            notifyResponse            = http.request(settings['method'], notifyUrl) 
            httpStatus                = notifyResponse.status

        except Exception as err: 
            httpStatus = 500

        response['http_response'] = httpStatus

        return response
        
