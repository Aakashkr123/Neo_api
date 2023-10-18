import requests
import json
import six
import re

class RestClientObject(object):

    def __init__(self,configuration) -> None:
        self.configuration = configuration

    def request(self,method,url,query_param=None,headers=None,body=None):
        '''Perform a request to to REST API

        :param method: HTTP request method (GET,POST,PUT,DELET etc)
        :param url: URL endpoint of request (https://www.google.com/)
        :param query_param:  (optional) query parameters of a url (?name=xyz&pass=234)
        :param headers: (optional) headers which will sent to API
        :param body: (optional) request body/data of API

        :raise: RequestException in case of request error
        '''

        method = method.upper()
        assert method in ['GET','POST','PUT','DELETE','HEAD','OPTIONS','PATCH']

        headers = headers or {}

        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        
        #add query_params if any required
        if query_param:
            url += '?' + six.moves.urllib.parse.urlencode(query_param)

        request_body = {}

        json_in_content = re.search('json',headers['Content-Type'],re.IGNORECASE)
        urlencoding_in_content = re.search('x-www-form-urlencoded',headers['Content-Type'],re.IGNORECASE)

        if json_in_content and body:
            request_body = json.dumps(body)
        elif urlencoding_in_content and body:
            request_body['jData'] = json.dumps(body)
        elif not json_in_content and not urlencoding_in_content:
            raise ValueError('Expected json/x-www-form-urlencoded in Content-Type')
        
        r = requests.request(method,url,headers=headers,data=request_body)
        
        return r
        

