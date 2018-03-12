import json
import requests


class CurrencyConverter:
    def __init__(self, config):
        self.__fiat_rate_api = config['fiat_rate_api']
        self.__fiat_symbol = config['fiat_symbol']
        self.fiat_rate = config['fiat_start_price']

        if not config['offline']:
            self.update_fiat_rate()

    def update_fiat_rate(self):
        try:
            res = requests.get(self.__fiat_rate_api, timeout=1).json()
            self.fiat_rate = res['rates'][self.__fiat_symbol]
        except Exception:
            print('update_fiat_rate exception:\n' + str(e) + '\n')
