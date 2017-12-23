from .market import Market
import requests


class Agent:
    def __init__(self, config, offline):
        self.fiat_rate_api = config['fiat_rate_api']
        self.fiat_symbol = config['fiat_symbol']
        self.fiat_rate = config['fiat_start_price']
        self.can_buy = True
        self.source_market = Market(config['source'], offline)
        self.destination_market = Market(config['destination'], offline)
        self.minimum_ratio_difference = config['minimum_ratio_difference']
        if offline:
            self.samples_count = min(len(self.source_market.db_data), len(self.destination_market.db_data))



    def get_market_price(self, market):
        if market == 'source':
            return self.convert_prices(self.source_market.get_prices(), self.fiat_rate)
        else:
            return self.destination_market.get_prices()

    def update_fiat_rate(self):
        try:
            res = requests.get(self.fiat_rate_api).json()
            self.fiat_rate = res['rates'][self.fiat_symbol]
        except Exception:
            pass

    def convert_prices(self, prices, rate):
        self.update_fiat_rate()
        return prices.update((key, value / rate) for key, value in prices.items())
