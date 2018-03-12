from .market import Market
import requests


class Agent:
    def __init__(self, config, db, currency_converter, offline):
        self.can_buy = True
        self.source_market = Market(config['source'], db, offline)
        self.destination_market = Market(config['destination'], db, offline)
        self.minimum_buy_ratio_difference = config['minimum_buy_ratio_difference']
        self.minimum_sell_ratio_difference = config['minimum_sell_ratio_difference']
        self.currency_converter = currency_converter
        self.offline = offline

        if offline:
            self.samples_count = min(self.source_market.object_count, self.destination_market.object_count)

    def get_market_prices(self, market):
        if market == 'source':
            return self.convert_prices(self.source_market.get_prices())
        else:
            return self.destination_market.get_prices()    

    def convert_prices(self, prices):
        if prices is not None:
            converted_prices = {}

            for key in prices:
                if key != 'date':
                    converted_prices[key] = prices[key] / self.currency_converter.fiat_rate
                else:
                    converted_prices[key] = prices[key]

            return converted_prices