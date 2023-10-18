from ksapi import KSAPI
from login_api import LoginObj

consumer_key = 'ABCDEFG'
consumer_secret = 'GYHTBDYWBS'
mobile_number = '+91XXXXXXXXX'
password = 'XXXXXXXXX'
mpin = '123456'

kotak = LoginObj(consumer_key,consumer_secret)
kotak.mobile_number = mobile_number
kotak.password = password
kotak.mpin = mpin

kotak.generate_session()


obj = KSAPI(kotak)

res = obj.get_order_book()
print(res)
