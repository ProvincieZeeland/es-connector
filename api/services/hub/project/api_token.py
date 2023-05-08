"""
**
*  Api_token
*
*  Support class for handling the authentication using the bearer token / secret
*
*  @author  Wim Kosten <w.kosten@zeeland.nl>
*
"""
class Api_token:
    
    """
    **
    *  getTokenFromHeaders
    *
    *  Attempt to extrect the bearer token/secret from the Authorization HTTP header
    *  and check if valid
    *
    *  @param  object request
    *  @return array
    *
    """
    def getTokenFromHeaders(request):

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
                    auth_token  = tokenParts[0]
                    auth_secret = tokenParts[1]

        # Validate the token and secret            
        if auth_token == False or auth_secret == False:
            validationInfo = {'status'    : 'failed',
                              'reason'    : 'Missing / invalid authorization token and/or secret',
                              'http_code' : 403}
        else:
            if auth_token == 'g88EfwFmBj0KOXwU0QVPloe1IHg6QtlFbD5wCRH0A' and auth_secret == 'secret':
                validationInfo = {'status'    : 'passed',
                                  'reason'    : 'Valid authorization token and secret',
                                  'http_code' : 200}
            else:
                validationInfo = {'status'    : 'failed',
                                  'reason'    : 'Incorrect authorization token and/or secret',
                                  'http_code' : 401}                                  

        return validationInfo
