import base64
import json
import datetime
import jwt
import os
import restv2


class LoginObj:

    api_endpoints = {
        'api.accesstoken':'https://napi.kotaksecurities.com/oauth2/token',
        'api.login':'https://gw-napi.kotaksecurities.com/login/1.0/login/v2/validate',
        'api.generateotp':'https://gw-napi.kotaksecurities.com/login/1.0/login/otp/generate',
        'api.placeorder':'https://gw-napi.kotaksecurities.com/Orders/2.0/quick/order/rule/ms/place',
        'api.orderhistory':'https://gw-napi.kotaksecurities.com/Orders/2.0/quick/order/history',
        'api.orderBook':'https://gw-napi.kotaksecurities.com/Orders/2.0/quick/user/orders',
        'api.cancelOrder':'https://gw-napi.kotaksecurities.com/Orders/2.0/quick/order/cancel',
        'api.tradereport':'https://gw-napi.kotaksecurities.com/Orders/2.0/quick/user/trades',
        'api.position':'https://gw-napi.kotaksecurities.com/Orders/2.0/quick/user/positions',
        'api.holdings':'https://gw-napi.kotaksecurities.com/Portfolio/1.0/portfolio/v1/holdings',
        'api.margin':'https://gw-napi.kotaksecurities.com/Orders/2.0/quick/user/check-margin',
        
        }

    def __init__(self,consumer_key=None,consumer_secret=None,access_token=None,neo_fin_key=None) -> None:
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.bearer_token = access_token
        self.base64_token = self.convert_base64()
        self.view_token = None
        self.sid = None
        self.user_id = None
        self.edit_token = None
        self.edit_sid = None
        self.edit_rid = None
        self.serverId = None
        self.login_param = None
        self.neo_fin_key = neo_fin_key or "X6Nk8cQhUgGmJ2vBdWw4sfzrz4L5En"
        self.final_headers = {}
        self.restclient = restv2.RestClientObject('No_configuration')

        self.mpin = 'XXXXXX'
        self.mobile_number = '+91XXXXXXXXXX'
        self.password = 'XXXXXXXXX'    

    def convert_base64(self):
        '''
        : Base64 Token Generator :
        This Funcion is used to generate base64 token after combining consumer_key and secret
        which is used to generate accesstoken/bearertoken
        '''
        base64_token = str(self.consumer_key + ':' + self.consumer_secret)
        encoded_token = base64_token.encode('ascii')
        base64_bytes = base64.b64encode(encoded_token)
        final_base64_token = base64_bytes.decode('ascii')
        return final_base64_token
    
    def get_userId(self):

        if not self.view_token:
            raise Exception({'error':[11004,'View_token not availble\nKindly add view token then execute this function']})
        
        jwt_token = jwt.decode(self.view_token, options={"verify_signature": False})
        self.user_id = jwt_token.get('sub')
        return self.user_id
    
    def requestHeaders(self):
        return {
            'Authorization': "Bearer " + self.bearer_token,
            "Sid": self.edit_sid,
            "Auth": self.edit_token,
            "neo-fin-key": self.neo_fin_key,
            "Content-Type": "application/x-www-form-urlencoded"}
    
    def get_access_token(self):
        header_params = {'Authorization': "Basic " + self.base64_token}
        body_params = {"grant_type": "client_credentials",}

        URL = self.api_endpoints.get('api.accesstoken')

        response = self.restclient.request(method='POST',url=URL,
                                           headers=header_params,body=body_params)

        self.bearer_token = response.json()['access_token']

    def get_view_token(self,mobile_number=None,password=None,pan=None,mpin=None):
        if not mobile_number and not password:
            raise ValueError('Please provide any (Mobile_number with +91 and password) or (mpin and pan)')
        
        requst_body = {"mobileNumber": mobile_number,"password": password}
        headers = {'Authorization': 'Bearer '+ self.bearer_token}
        response = self.restclient.request(method='POST',url=self.api_endpoints.get('api.login'),
                                           headers=headers,body=requst_body)
        
        #this view_token will be used filnal generate session function in (Auth:view_token)
        self.view_token = response.json()['data']['token']
        self.sid = response.json()['data']['sid']
        self.serverId = response.json()['data']['hsServerId']

    def get_otp_request(self):
        userId = self.user_id or self.get_userId()
        headers = {'Authorization': 'Bearer '+ self.bearer_token}
        request_body = {"userId": userId,"sendEmail": False,"isWhitelisted": True}
        request_otp_response =  self.restclient.request(method='POST',url=self.api_endpoints.get('api.generateotp'),
                                                        headers=headers,body=request_body)
        print(request_otp_response.json())

    def generate_session(self):

        if self._check_cache_memory():
            print('Logged Into KotakAPI')
            return 'Login Done Start Trading...'

        if not self.edit_token and not self.edit_sid and not self.bearer_token:

            self.get_access_token()
            self.get_view_token(self.mobile_number,self.password)
            self.get_otp_request()


            request_body = {'userId':self.user_id,'mpin': self.mpin }
            headers = {'Authorization':'Bearer '+ self.bearer_token,'Auth': self.view_token,'sid':self.sid}

            response = self.restclient.request(method='POST',url=self.api_endpoints.get('api.login'),
                                                       headers=headers,body=request_body)
            print(response)
            print(response.text)
            
            self.edit_token = response.json().get('data')['token']
            self.edit_sid = response.json().get('data')['sid']
            self.serverId = response.json().get('data')['hsServerId']

            self._save_login_details()

            return
        
    def _check_cache_memory(self):
        try:
            if 'auth.json' in os.listdir():
                with open('auth.json','r') as f:
                    data = json.loads(f.read())
                if int(data.get('expire')) < datetime.datetime.now().timestamp():
                    return False
                self.bearer_token = data.get('Authorization')
                self.edit_sid = data.get('Sid')
                self.edit_token = data.get('Auth')
                self.serverId = data.get('serverId')
                return True
            
            return False
        except Exception as e:
            print(e)
            return False

    def _save_login_details(self):

        next_interval = (datetime.datetime.now() + datetime.timedelta(days=1))
        expire = next_interval.replace(minute=0,hour=0,second=0).timestamp()

        res = self.requestHeaders()
        res['Authorization'] = self.bearer_token
        res['expire'] = expire
        res['serverId'] = self.serverId


        with open('auth.json','w') as f:
            f.write(json.dumps(res))
            return
        


        

        

            
        
        
        
