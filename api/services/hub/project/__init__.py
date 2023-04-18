##############################################################################
#  
#  HUB
#
#  API for notifying extenal sources of a change
#
#  @author Wim Kosten <w.kosten@zeeland.nl>
#
##############################################################################

# Import operating system interfaces  
import os

# Import Flask / Flask swagger support
from flask import Flask, jsonify, request, make_response, json

# Import wraps so we can use the Python decorators 
from functools import wraps

# custom stuff
from .decorators import validateBearerToken
from .api_notify import Api_notify

# Set app
app = Flask(__name__)


##############################################################################
#  
#  heartbeat
#
#  Heartbeat function to check if client still responding (green unicorn / Docker healthcheck)
#
#  @param void
#  @return void
#
##############################################################################
@app.route("/heartbeat", methods=['GET'])
def route_handler_heartbeat():
    environmentName = os.getenv('ES_ENVIRONMENT_NAME')
    return make_response("OK from HUB:"+environmentName), 200


##############################################################################
#  
#  notify
#
#  Notify external systems of a change
#
#  @param string action (create/update/delete)
#  @param string object_id
#  @return json response
#
##############################################################################
@app.route("/notify/", methods=['GET'], defaults={'object_id': '', 'action':''})
@app.route("/notify/<action>", methods=['GET'], defaults={'object_id': ''})
@app.route("/notify/<object_id>", methods=['GET'], defaults={'action': ''})
@app.route("/notify/<action>/<object_id>", methods=['GET'])
#@validateBearerToken
def route_handler_notify(action, object_id):

    responses = {}

    # check if we have an objectid
    if object_id == "" or action == "":
        response = {"status"    :"fout",
                    "reason"    :"Geen actie en/of object_id gespecificeerd (/notify/<action>/<objectid>)",
                    "http_code" : 500}
        return make_response(jsonify(response)), 500


    # get external parties to notify
    notifiers = Api_notify.getNotificationEndpoints()

    # check if we have notifiers
    if (len(notifiers) == 0):
        response = {"status"    :"fout",
                    "reason"    :"Geen notificatie endpoints gedefinieerd",
                    "http_code" : 409}
        return make_response(jsonify(response)), 409    

    #  Loop notifiers and call endpoints
    for notify_alias in notifiers.keys():
        responses[notify_alias] = Api_notify.dispatch(action, object_id, notifiers[notify_alias])

    #response = {'endpoints' : notifiers}
    return make_response(jsonify(responses)), 200



