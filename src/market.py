import requests
from pymongo import MongoClient


class Market:
    def __init__(self, config):
        self.market = config['market']
        self.symbol = config['symbol']
        self.api = config['api']
        self.last_price_key = config['last_price_key']

    def get_price(self):
        try:
            res = requests.get(self.api).json()
            last_price = res[self.last_price_key]
            return self.convert_symbols(float(last_price))
        except:
            return None

    def convert_symbols(self, price):
        if self.symbol == 'BTCNIS':
            return price / 3.49
        else:
            return price


class OfflineMarket(Market):
    def __init__(self, config):
        super().__init__(config)
        self.client = MongoClient('mongodb://ariel:ariel@ds127536.mlab.com:27536/collector')
        self.db = self.client.collector
        self.prices = self.db[self.market.lower()].find({})
        self.object_count = self.db[self.market.lower()].count()

    def get_offline_price(self, index):
        try:
            return super().convert_symbols(float(self.prices[index]['price']))
        except:
            return None
