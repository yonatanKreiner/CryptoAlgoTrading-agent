import json
import requests


class CurrencyConverter:
    def __init__(self):
        config = json.load(open('src/agent_config.json'))
        self.fiat_rate_api = config['fiat_rate_api']
        self.fiat_symbol = config['fiat_symbol']
        self.fiat_rate = config['fiat_start_price']
        self.get_rate()

    def get_rate(self):
        try:
            res = requests.get(self.fiat_rate_api).json()
            self.fiat_rate = res['rates'][self.fiat_symbol]
        except Exception:
            pass

        return self.fiat_rate
