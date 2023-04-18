# Import Blueprint / make_response
from flask import Blueprint, make_response, jsonify

# Import our decorator used for token validation
from ..models.decorators import validateBearerToken

# Import os
import os

# Create blueprint
bp_general = Blueprint('general', __name__)

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
@bp_general.route("/heartbeat", methods=['GET'])
def route_handler_heartbeat():
    environmentName = os.getenv('ES_ENVIRONMENT_NAME')
    return make_response("OK from "+environmentName), 200

    
##############################################################################
#  
#  validateBearerToken
#
#  Validate the token by a HTTP request
#
#  @param void
#  @return void
#
##############################################################################
@bp_general.route("/tokentest", methods=['GET'])
@validateBearerToken
def route_handler_tokentest():

    # Check for the auth header
    response = {'status'    : 'passed',
                'reason'    : 'Valid authorization token and secret',
                              'http_code' : 200}
    return make_response(jsonify(response)), 200

