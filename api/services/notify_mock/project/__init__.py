##############################################################################
#  
#  Notify_mock
#
#  Mock container for testing several notification methods
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

# Set app
app = Flask(__name__)


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
def route_handler_notify(action, object_id):

    # check if we have an objectid
    if object_id == "" or action == "":
        response = {"status"    :"failed",
                    "reason"    :"Geen actie en/of object_id gespecificeerd (/notify/<action>/<objectid>)",
                    "http_code" : 500}
        return make_response(jsonify(response)), 500

    response = {'what' : 'notify'}
    return make_response(jsonify(response)), 200


##############################################################################
#  
#  notify_post
#
#  Notify external systems of a change
#
#  @param string action (create/update/delete)
#  @param string object_id
#  @return json response
#
##############################################################################
@app.route("/notify_post/", methods=['POST'], defaults={'object_id': '', 'action':''})
@app.route("/notify_post/<action>", methods=['POST'], defaults={'object_id': ''})
@app.route("/notify_post/<object_id>", methods=['POST'], defaults={'action': ''})
@app.route("/notify_post/<action>/<object_id>", methods=['POST'])
def route_handler_notify_post(action, object_id):

    # check if we have an objectid
    if object_id == "" or action == "":
        response = {"status"    :"failed",
                    "reason"    :"Geen actie en/of object_id gespecificeerd (/notify/<action>/<objectid>)",
                    "http_code" : 500}
        return make_response(jsonify(response)), 500

    response = {'what' : 'notify_post'}
    return make_response(jsonify(response)), 200


##############################################################################
#  
#  notify_bearer
#
#  Notify external systems of a change
#
#  @param string action (create/update/delete)
#  @param string object_id
#  @return json response
#
##############################################################################
@app.route("/notify_bearer/", methods=['GET'], defaults={'object_id': '', 'action':''})
@app.route("/notify_bearer/<action>", methods=['GET'], defaults={'object_id': ''})
@app.route("/notify_bearer/<object_id>", methods=['GET'], defaults={'action': ''})
@app.route("/notify_bearer/<action>/<object_id>", methods=['GET'])
#@validateBearerToken
def route_handler_notify_bearer(action, object_id):

    # check if we have an objectid
    if object_id == "" or action == "":
        response = {"status"    :"failed",
                    "reason"    :"Geen actie en/of object_id gespecificeerd (/notify/<action>/<objectid>)",
                    "http_code" : 500}
        return make_response(jsonify(response)), 500

    response = {'what' : 'notify_bearer'}
    return make_response(jsonify(response)), 200


##############################################################################
#  
#  notify_basic_auth
#
#  Notify external systems of a change
#
#  @param string action (create/update/delete)
#  @param string object_id
#  @return json response
#
##############################################################################
@app.route("/notify_basic_auth/", methods=['GET'], defaults={'object_id': '', 'action':''})
@app.route("/notify_basic_auth/<action>", methods=['GET'], defaults={'object_id': ''})
@app.route("/notify_basic_auth/<object_id>", methods=['GET'], defaults={'action': ''})
@app.route("/notify_basic_auth/<action>/<object_id>", methods=['GET'])
#@validateBearerToken
def route_handler_notify_basic_auth(action, object_id):

    # check if we have an objectid
    if object_id == "" or action == "":
        response = {"status"    :"failed",
                    "reason"    :"Geen actie en/of object_id gespecificeerd (/notify/<action>/<objectid>)",
                    "http_code" : 500}
        return make_response(jsonify(response)), 500

    response = {'what' : 'notify_basic_auth'}
    return make_response(jsonify(response)), 200


