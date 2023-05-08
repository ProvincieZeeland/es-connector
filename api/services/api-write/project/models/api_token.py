import os
import json
from dotenv import load_dotenv
from .utils import readConfigFile

##############################################################################
#  
#  Api_token
#
#  Class for handling tokens
#
#  @author Wim Kosten <w.kosten@zeeland.nl>
#
##############################################################################

class Api_token:
    
    ##############################################################################
    #  
    #  getTokenFromHeaders
    #
    #  Extract the token from the HTTP header
    #
    #  @param request
    #  @return array
    #
    ##############################################################################
    def getTokenFromHeaders(request):

        load_dotenv()

        auth_header = request.headers.get('Authorization')
        auth_token  = False
        auth_secret = False

        # If we have the header, extract the token and secret
        if auth_header:
            rawToken = auth_header.split(" ")
            
            if len(rawToken) == 2:
                token      = rawToken[1]
                tokenParts = token.split(":")

                if len(tokenParts) == 2:    
                    auth_token = tokenParts[0]
                    auth_user  = tokenParts[1]

        # Validate the token and secret            
        if auth_token == False or auth_user == False:
            validationInfo = {'status'    : 'failed',
                              'reason'    : 'Token en/of secret is niet correct',
                              'http_code' : 403}
        else:

            # get tokens
            try:
                config = readConfigFile()

                if ("es-connector" in config) and ("tokens" in config['es-connector']):
                    tokens  = config['es-connector']['tokens']

                    if auth_user in tokens:
                        valid_token = tokens[auth_user]

                    else:
                        return {'status'    : 'failed',
                                'reason'    : 'Token en/of secret is niet correct',
                                'http_code' : 401}         
                else:
                    return {'status'    : 'failed',
                            'reason'    : 'Configuratie niet gevonden',
                            'http_code' : 500}                                               
            
                if auth_token == valid_token:
                    validationInfo = {'status'    : 'passed',
                                      'reason'    : '',
                                      'http_code' : 200}
                else:
                    validationInfo = {'status'    : 'failed',
                                      'reason'    : 'Token en/of secret is niet correct',
                                      'http_code' : 401}                                  
            except Exception as e: 
                    validationInfo = {'status'    : 'failed',
                                      'reason'    : 'Token en/of secret is niet correct',
                                      'http_code' : 500}  

        return validationInfo
