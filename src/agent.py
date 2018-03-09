from .market import Market
import requests


class Agent:
    def __init__(self, config, db, offline):
        self.fiat_rate_api = config['fiat_rate_api']
        self.fiat_symbol = config['fiat_symbol']
        self.fiat_rate = config['fiat_start_price']
        self.can_buy = True
        self.source_market = Market(config['source'], db, offline)
        self.destination_market = Market(config['destination'], db, offline)
        self.minimum_buy_ratio_difference = config['minimum_buy_ratio_difference']
        self.minimum_sell_ratio_difference = config['minimum_sell_ratio_difference']
        self.offline = offline
        self.update_fiat_rate()

        if offline:
            self.samples_count = min(self.source_market.object_count, self.destination_market.object_count)

    def get_market_prices(self, market):
        if market == 'source':
            return self.convert_prices(self.source_market.get_prices())
        else:
            return self.destination_market.get_prices()

    def update_fiat_rate(self):
        try:
            res = requests.get(self.fiat_rate_api, timeout=0.5).json()
            self.fiat_rate = res['rates'][self.fiat_symbol]
        except Exception as e:
            print('update_fiat_rate exception:\n' + str(e) + '\n')

    def convert_prices(self, prices):
        if not self.offline:
            self.update_fiat_rate()

        if prices is None:
            return None

        converted_prices = {}

        for key in prices:
            if key != 'date':
                converted_prices[key] = prices[key] / self.fiat_rate
            else:
                converted_prices[key] = prices[key]

        return converted_prices