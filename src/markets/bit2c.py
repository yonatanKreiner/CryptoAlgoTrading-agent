import base64
import hashlib
import hmac
import time
import requests

from ..utils.currency_converter import CurrencyConverter


class Bit2cClient:
    def __init__(self, base_url, key, secret):
        self.key = key
        self.secret = secret
        self.base_url = base_url
        self.currency_converter = CurrencyConverter()
        self.last_nonce = 0

    @staticmethod
    def add_nonce_to_params(params, nonce):
        if params == '':
            return 'nonce=' + nonce
        else:
            return params + '&nonce=' + nonce

    def compute_hash(self, params):
        return base64.b64encode(hmac.new(bytearray(self.secret.upper(), "ASCII"), bytearray(params, "ASCII"),
                                         hashlib.sha512).digest()).decode("ASCII").replace("\n", "")

    def query(self, method, url, params):
        nonce = int(time.time())

        if nonce <= self.last_nonce:
            #nonce += 1
            nonce = self.last_nonce + 1

        self.last_nonce = nonce
        params_with_nonce = self.add_nonce_to_params(params, str(nonce))

        sign = self.compute_hash(params_with_nonce)
        headers = {'Key': self.key, 'Sign': sign, 'Content-Type': 'application/x-www-form-urlencoded'}

        res = None

        try:
            if method == 'GET':
                res = requests.get(self.base_url + url + '?' + params_with_nonce, headers=headers, timeout=10)
            elif method == 'POST':
                res = requests.post(self.base_url + url, data=params_with_nonce, headers=headers, timeout=10)
        except Exception as e:
            print('bit2c query: ' + url + ' exception\n' + str(e))

        return res.json()

    def get_balance(self):
        return self.query('GET', '/Account/Balance', "")

    def add_order(self, params):
        data = 'Amount=' + str(params["Amount"]) + \
               '&Price=' + str(params["Price"]) + \
               '&IsBid=' + str(params["IsBid"]) + '&Pair=BtcNis'

        return self.query('POST', '/Order/AddOrder', data)

    def sell_order(self, amount):
        data = 'Amount=' + str(amount) + '&Pair=BtcNis'

        return self.query('POST', '/Order/AddOrderMarketPriceSell', data)

    def get_order(self, order_id):
        return self.query('GET', '/Order/GetById', "id=" + str(order_id))

    def cancel_order(self, order_id):
        return self.query('POST', '/Order/CancelOrder', "id=" + str(order_id))
