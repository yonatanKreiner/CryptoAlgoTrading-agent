import requests


class Agent:
    def __init__(self, config):
        self.can_buy = True
        self.source_market = Market(config['source'])
        self.destination_market = Market(config['destination'])

        self.minimum_ratio_difference = config['minimum_ratio_difference']

    def get_market_price(self, market):
        if market == 'source':
            return self.source_market.get_price()
        else:
            return self.destination_market.get_price()


class Market:
    def __init__(self, config):
        self.market = config['market']
        self.symbol = config['symbol']
        self.api = config['api']
        self.last_price_key = config['last_price_key']

    def get_price(self):
        res = requests.get(self.api).json()
        last_price = res[self.last_price_key]

        if last_price is not None:
            return self.convert_symbols(float(last_price))

    def convert_symbols(self, price):
        if self.symbol == 'BTCNIS':
            return price / 3.49
        else:
            return price
