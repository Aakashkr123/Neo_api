from login_api import LoginObj
from restv2 import RestClientObject
from neo_api_client import settings
from neo_api_client import req_data_validation
from pprint import pprint

class KSAPI:

    def __init__(self,configuration:LoginObj=None) -> None:
        self.configuration = configuration
        # self.configuration.generate_session()
        self.rest = RestClientObject(self.configuration)

    def place_order(self, exchange_segment, product, price, order_type, quantity, validity, trading_symbol,
                      transaction_type, amo="NO", disclosed_quantity="0", market_protection="0", pf="N",
                      trigger_price="0", tag=None):
        
        req_data_validation.place_order_validation(exchange_segment, product, price, order_type, quantity,
                                                    validity,trading_symbol, transaction_type)
        
        exchange_segment = settings.exchange_segment[exchange_segment]
        product = settings.product[product]
        order_type = settings.order_type[order_type]

        headers = self.configuration.requestHeaders()
        request_body = {"am": amo, "dq": disclosed_quantity, "es": exchange_segment, "mp": market_protection, 
                        "pc": product, "pf": pf, "pr": price, "pt": order_type, "qt": quantity, "rt": validity,
                        "tp": trigger_price, "ts": trading_symbol, "tt": transaction_type, "ig": tag}
        
        query_param = {"sId": self.configuration.serverId}

        url = self.configuration.api_endpoints.get('api.placeorder')

        response = self.rest.request(method='POST', url=url, query_param=query_param,
                                     headers=headers, body=request_body)
        return response

    def place_market_buy(self, quantity, trading_symbol,
                         exchange_segment = "NSE",validity = "DAY",product = "MIS",price = "0",
                         order_type = "MKT",transaction_type = "B"):
        
        response = self.place_order(exchange_segment,product,price,order_type,
                                    quantity,validity,trading_symbol,
                                    transaction_type)
        return response
    
    def place_market_sell(self, quantity, trading_symbol,
                          exchange_segment = "NSE",validity = "DAY",product = "MIS",price = "0",
                          order_type = "MKT",transaction_type = "S"):
        
        response = self.place_order(exchange_segment,product,price,order_type,
                                    quantity,validity,trading_symbol,
                                    transaction_type)
        return response

    def place_limit_buy(self,
                        price,
                        quantity,
                        trading_symbol,
                        exchange_segment="NSE",
                        validity="DAY"):
        
        product = "MIS",
        order_type = "Limit",
        transaction_type = "B"

        response = self.place_order(exchange_segment,product,price,order_type,
                                    quantity,validity,trading_symbol,
                                    transaction_type)
        return response
    
    def place_limit_sell(self, price, quantity, trading_symbol,
                        exchange_segment = "NSE",validity = "DAY"):
        
        product = "MIS"
        order_type = "Limit"
        transaction_type = "S"

        response = self.place_order(exchange_segment,product,price,order_type,
                                    quantity,validity,trading_symbol,
                                    transaction_type)
        return response
        
    def place_stop_buy(self,price,tp,quantity,trading_symbol,
                       validity = "DAY",
                       exchange_segment = "NSE"):
        
        product = "MIS"
        order_type = "SL"
        transaction_type = "B"

        response = self.place_order(exchange_segment,product,price,order_type,quantity,validity,
                                    trading_symbol,transaction_type,trigger_price=tp)
        return response

    def place_stop_sell(self,price,tp,quantity,trading_symbol,
                        exchange_segment = "NSE",validity = "DAY"):
        
        product = "MIS"
        order_type = "SL"
        transaction_type = "S"

        response = self.place_order(exchange_segment,product,price,order_type,quantity,validity,
                                    trading_symbol,transaction_type,trigger_price=tp)
        return response

    def place_stop_market_buy(self,tp,quantity,trading_symbol,
                              exchange_segment = "NSE",validity = "DAY",product = "MIS",
                              price = "0",order_type = "SL-M",transaction_type = "B"):

        response = self.place_order(exchange_segment,product,price,order_type,quantity,validity,
                                    trading_symbol,transaction_type,trigger_price=tp)
        return response

    def place_stop_market_sell(self,tp,quantity,trading_symbol,
                               exchange_segment = "NSE",validity = "DAY",product = "MIS",
                               price = "0",order_type = "SL-M",transaction_type = "S"):
        
        response = self.place_order(exchange_segment,product,price,order_type,quantity,validity,trading_symbol,
                                    transaction_type,trigger_price=tp)
        return response

    def cancel_order(self,orderId,amo="NO"):
        body_params = {"on": str(orderId), "amo": amo}
        headers = self.configuration.requestHeaders()
        query_params = {"sId": self.configuration.serverId}
        url = self.configuration.api_endpoints.get('api.cancelOrder')

        res = self.rest.request(method='POST',url=url,query_param=query_params,
                                headers=headers,body=body_params)   
        return res

    def get_order_book(self):
        query_param = {"sId": self.configuration.serverId}
        headers = self.configuration.requestHeaders()
        url = self.configuration.api_endpoints.get('api.orderBook')
        res = self.rest.request('GET',url,query_param,headers)
        return res

    def get_order_history(self,orderId):
        header_param = self.configuration.requestHeaders()
        header_param['accept'] = 'application/json'

        body = {'nOrdNo':str(orderId)}
        query_param =  {"sId": self.configuration.serverId}

        url = self.configuration.api_endpoints.get('api.orderhistory')
        res = self.rest.request(method="POST",url=url,query_param=query_param,
                                headers=header_param,body=body)
        return res

    def get_trade_report(self):
        header_param = self.configuration.requestHeaders()
        header_param['accept'] = 'application/json'
        query_param =  {"sId": self.configuration.serverId}
        url = self.configuration.api_endpoints.get('api.tradereport')
        response = self.rest.request('GET',url,query_param,header_param)
        return response

    def margin(self,instrument_token , quantity, transaction_type, exchange_segment='NSE', price="0",
               order_type='MKT', product='MIS',trigger_price=None, broker_name="KOTAK", branch_id="ONLINE",
               stop_loss_type=None, stop_loss_value=None, square_off_type=None, square_off_value=None,
               trailing_stop_loss=None, trailing_sl_value=None):
        
        req_data_validation.margin_validation(exchange_segment,price,order_type,product,quantity,instrument_token,
                                              transaction_type)
        
        exchange_segment = settings.exchange_segment[exchange_segment]
        product = settings.product[product]
        order_type = settings.order_type[order_type]
        
        body_params = {"exSeg": exchange_segment, "prc": price, "prcTp": order_type, "prod": product, "qty": quantity,
                       "tok": instrument_token, "trnsTp": transaction_type, "trgPrc": trigger_price,
                       "brkName": broker_name, "brnchId": branch_id, "slAbsOrTks": stop_loss_type,
                       "slVal": stop_loss_value, "sqrOffAbsOrTks": square_off_type, "sqrOffVal": square_off_value,
                       "trailSL": trailing_stop_loss, "tSLTks": trailing_sl_value}
        
        header_param = self.configuration.requestHeaders()

        query_param =  {"sId": self.configuration.serverId}

        url = self.configuration.api_endpoints.get('api.margin')

        response = self.rest.request('POST',url,query_param,header_param,body_params)
        
        return response
        

    def get_position(self):
        headers = self.configuration.requestHeaders()
        query_param = {'sId':self.configuration.serverId}
        url = self.configuration.api_endpoints.get('api.position')
        res = self.rest.request('GET',url,query_param,headers)
        return res