from .market import Market, OfflineMarket
import requests


class Agent:
    def __init__(self, config):
        self.fiat_rate_api = config['fiat_rate_api']
        self.fiat_symbol = config['fiat_symbol']
        self.fiat_rate = 0
        self.can_buy = True
        self.source_market = Market(config['source'])
        self.destination_market = Market(config['destination'])

        self.minimum_ratio_difference = config['minimum_ratio_difference']

    def get_market_prices(self, market):
        if market == 'source':
            return self.convert_prices(source_market.get_prices(), self.fiat_rate)
        else:
            return self.destination_market.get_prices()

    def update_fiat_rate(self):
        try:
            res = requests.get(self.fiat_rate_api).json()
            self.fiat_rate = res['rates'][self.fiat_symbol]
        except Exception:
            pass

    @staticmethod
    def convert_prices(prices, rate):
        return prices.update((key, value / rate) for key, value in prices.items())


class OfflineAgent:
    def __init__(self, config):
        self.can_buy = True
        self.source_market = OfflineMarket(config['source'])
        self.destination_market = OfflineMarket(config['destination'])
        self.object_count = min((self.source_market.object_count, self.destination_market.object_count))

        self.minimum_ratio_difference = config['minimum_ratio_difference']

    def get_market_price(self, market, index):
        if market == 'source':
            return self.source_market.get_offline_price(index)
        else:
            return self.destination_market.get_offline_price(index)
