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
        self.price_types = {
            'last': config['last_price_key'],
            'bid': config['bid_key'],
            'ask': config['ask_key']
        }
        self.buy_fee = config['buy_fee']
        self.sell_fee = config['sell_fee']

    def get_price(self, type):
        try:
            res = requests.get(self.api).json()
            last_price = res[self.last_price_key]
            price = res[self.price_types[type]]
            return self.convert_symbols(float(last_price))
        except:
            return None

    def convert_symbols(self, price):
        if self.symbol == 'BTCNIS':
            return price / 3.49
        else:
            return price
