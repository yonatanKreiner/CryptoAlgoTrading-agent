import requests
from pymongo import MongoClient


class Market:
    def __init__(self, config, offline):
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
        self.offline = offline

        if self.offline:
            self.__initialize_prices()

    def __initialize_prices(self):
        client = MongoClient('mongodb://ariel:ariel@ds127536.mlab.com:27536/collector')
        db = client.collector
        self.db_data = [x for x in db[self.market.lower()].find({}, {'price': 1, 'bid': 1, 'ask': 1, 'date': 1, '_id': False})]
        self.object_count = db[self.market.lower()].count()
        self.index = 0

    def get_prices(self):
        try:
            if self.offline:
                res = self.db_data[self.index]
                self.index += 1
                prices = {
                    'last': res['price'],
                    'bid': res['bid'],
                    'ask': res['ask'],
                    'date': res['date']
                }
            else:
                res = requests.get(self.api).json()
                prices = {
                    'last': float(res[self.price_types['last']]),
                    'bid': float(res[self.price_types['bid']]),
                    'ask': float(res[self.price_types['ask']])
                }

            return prices
        except Exception:
            return None
