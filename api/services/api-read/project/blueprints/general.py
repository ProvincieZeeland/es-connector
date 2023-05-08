# Import Blueprint / make_response
from flask import Blueprint, make_response, jsonify

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

