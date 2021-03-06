import hashlib,mimetypes,magic
from rumahiot_lemari.settings import VALID_MONTHS

class ResponseGenerator():
    # generate error response in dict format
    def error_response_generator(self,code, message):
        response = {
            "error": {
                "code": code,
                "message": message
            }
        }
        return response

    # generate data response in dict format
    # input parameter data(dict)
    def data_response_generator(self,data):
        response = {
            "data": data
        }
        return response

    # generate error response in dict format
    def success_response_generator(self,code, message):
        response = {
            "success": {
                "code": code,
                "message": message
            }
        }
        return response


class LemariUtils():

    # get object file_type
    # for inmemoryuploadedfile

    def get_file_type(self,inmemoryuploadedfile):
        return mimetypes.MimeTypes().types_map_inv[1][magic.from_buffer(inmemoryuploadedfile.read(), mime=True)][0]

    def integer_check(self, value):
        try :
            int(value)
        except ValueError:
            return False
        else:
            return True


class RequestUtils():
    # get access token from authorization header
    # input parameter : request(request)
    # return :  data['token'] = token, when the header format is correct (string)
    #           data['error'] = None, when the header format is correct
    #           data['token'] = None, when the header format is incorrect
    #           data['error'] = Error, when the header format is incorrect(string)
    # data = {
    #     'token' : token(string),
    #     'error' : error(string)
    # }
    def get_access_token(self, request):
        data = {}
        auth_header = request.META['HTTP_AUTHORIZATION'].split()
        # verify the authorization header length (including authorization type, currently using bearer)
        if len(auth_header) != 2:
            data['token'] = None
            data['error'] = 'Invalid authorization header length'
            return data
        else:
            # check for the type
            if auth_header[0].lower() != 'bearer':
                data['token'] = None
                data['error'] = 'Invalid authorization token method'
                return data
            else:
                data['token'] = auth_header[1]
                data['error'] = None
                return data