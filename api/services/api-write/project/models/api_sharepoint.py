import urllib3
import os
import io
import PyPDF2
import xmltodict

##############################################################################
#  
#  Api_sharepoint
#
#  API for getting a document from Sharapoint / extract text
#
#  @author Wim Kosten <w.kosten@zeeland.nl>
#
##############################################################################
class Api_sharepoint:


    ##############################################################################
    #  
    #  fileExistOnStorage
    #
    #  Check if a file exists on the storage
    #
    #  @param object_id
    #  @param fileExtension
    #  @return boolean
    #
    ##############################################################################
    def fileExistOnStorage(object_id, fileExtension):
    
        azureFile = os.getenv('SP_ENDPOINT')+object_id+'.'+fileExtension
        
        try:
            http           = urllib3.PoolManager()
            azureResponse  = http.request('HEAD', azureFile) 
            httpStatus     = azureResponse.status
            
            if (httpStatus == 200):
                return True
            else:
                return False    

        except Exception as e: 
            
            return False    
    
    
    ##############################################################################
    #  
    #  getFileFromStorage
    #
    #  Get a file from Sharepoint / Azure storage container
    #
    #  @param object_id
    #  @param fileExtension
    #  @return object
    #
    ##############################################################################
    def getFileFromStorage(object_id, fileExtension):

        azureFile = os.getenv('SP_ENDPOINT')+object_id+'.'+fileExtension
        
        try:
            http           = urllib3.PoolManager()
            azureResponse  = http.request('GET', azureFile) 
            rawData        = azureResponse.data

            return {"http_status" : azureResponse.status,
                    "error"       : "",
                    "contents"    : rawData,
                    "azure_link"  : azureFile}

        except Exception as e: 

            return {"http_status" : 500,
                    "error"       : "error getting document: "+azureFile,
                    "contents"    : "",
                    "azure_link"  : azureFile}



    ##############################################################################
    #  
    #  getMetadataFromStorage
    #
    #  Get the XML metadata from the storage and convert to JSON
    #
    #  @param object_id
    #  @return object
    #
    ##############################################################################
    def getMetadataFromStorage(object_id):

        # Set metadata url    
        azureFile = os.getenv('SP_ENDPOINT')+object_id+'.xml'

        # Attempt to get the XML file from the Azure storage container
        try:
            http           = urllib3.PoolManager()
            azureResponse  = http.request('GET', azureFile) 
            rawData        = azureResponse.data
            httpStatus     = azureResponse.status

            # Got the file ?
            if (httpStatus == 200):

                try:
                    xmlParsed = xmltodict.parse(rawData)
                    http      = 200
                except:            
                    http      = 418 

            # Nope, file resulted in a none http/200
            else:
                http = azureResponse.status

            return {"http_status" : http,
                    "contents"    : rawData,
                    "json"        : xmlParsed,
                    "azure_link"  : azureFile}   

        # Somewhere along the line it messed up
        except:
            return {"http_status" : 500,
                    "error"       : "error getting document: "+azureFile,
                    "contents"    : "",
                    "json"        : {},
                    "azure_link"  : azureFile}


    ##############################################################################
    #  
    #  extractTextFromExternalPDF
    #
    #  Retrieve an external PDF file and extract the text
    #
    #  @param object_id
    #  @param fileExtension
    #  @return object
    #
    ##############################################################################
    def extractTextFromExternalPDF(object_id):
        
        azureFile = os.getenv('SP_ENDPOINT')+object_id+'.pdf'
        
        try:
            http           = urllib3.PoolManager()
            azureResponse  = http.request('GET', azureFile) 

            if azureResponse.status != 200:
                return {"file"        : azureFile,
                        "size"        : "",
                        "pages"       : 0,
                        "body"        : "",
                        "http_status" : azureResponse.status}

            ioBytes        = io.BytesIO(azureResponse.data)
            pdfReader      = PyPDF2.PdfReader(ioBytes)
            pages          = len(pdfReader.pages)
            parts          = []
            body           = ""

            if (pages > 0):
                for i in range (pages):
                    page = pdfReader.pages[i]
                    parts.append(page.extract_text())

                body = "".join(parts)

            return {"file"        : azureFile,
                    "size"        : len(azureResponse.data),
                    "metadata"    : pdfReader.metadata,
                    "pages"       : pages,
                    "body"        : body,
                    "http_status" : 200}
        except Exception as err:
            #raise err
            return {"file"        : azureFile,
                    "size"        : "",
                    "pages"       : 0,
                    "body"        : "",
                    "http_status" : 409}
