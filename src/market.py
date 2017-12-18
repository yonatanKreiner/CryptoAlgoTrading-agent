import requests
from pymongo import MongoClient


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

    def get_prices(self):
        try:
            res = requests.get(self.api).json()
            return_value = {
                'last': res[self.price_types['last']],
                'bid': res[self.price_types['bid']],
                'ask': res[self.price_types['ask']]
            }
            return return_value
        except Exception:
            return None


class OfflineMarket(Market):
    def __init__(self, config):
        super().__init__(config)
        self.client = MongoClient('mongodb://ariel:ariel@ds127536.mlab.com:27536/collector')
        self.db = self.client.collector
        self.prices = [x['price'] for x in self.db[self.market.lower()].find({}, {'price': 1, '_id': False})]
        self.object_count = self.db[self.market.lower()].count()

    def get_offline_price(self, index):
        try:
            return super().convert_symbols(float(self.prices[index]))
        except:
            return None
