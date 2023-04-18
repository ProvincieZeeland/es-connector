import os
from functools import wraps
from .api_token import Api_token
from flask import jsonify, request, make_response, json

##############################################################################
#  
#  validateBearerToken
#
#  Decorator function to validate our bearer token
#
#  @param void
#  @return 
#
##############################################################################
def validateBearerToken(f):
   @wraps(f)
   def bearer_decorator(*args, **kwargs):

        # validate the token using our Api_token class
        tokenAuth = Api_token.getTokenFromHeaders(request)

        # if invalid token return error info
        if tokenAuth['http_code'] != 200:
            return make_response(tokenAuth), tokenAuth['http_code']

        # passed, continue with original function / flow
        return f(*args, **kwargs)

   return bearer_decorator
   
   
