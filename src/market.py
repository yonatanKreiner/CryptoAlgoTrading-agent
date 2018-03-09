from pymongo import MongoClient
from .utils.proxy import Proxy


class Market:
    def __init__(self, config, db, offline):
        self.market = config['market']
        self.symbol = config['symbol']
        self.api = config['api']
        self.price_types = {
            'last': config['last_price_key'],
            'bid': config['bid_key'],
            'ask': config['ask_key']
        }
        self.prices = {}
        self.offline = offline
        self.proxy = Proxy()
        self.db = db

        if self.offline:
            self.__initialize_prices()
            self.index = 0

    def __initialize_prices(self):
        self.db_data = [x for x in self.db.get_tickers(self.market.lower())]
        self.object_count = len(self.db_data)

    def get_prices(self):
        try:
            if self.offline:
                res = self.db_data[self.index]
                self.index += 1
                self.prices = {
                    'last': res['price'],
                    'bid': res['bid'],
                    'ask': res['ask'],
                    'date': res['date']
                }
            else:
                res = self.proxy.get(self.api).json()
                self.prices = {
                    'last': float(res[self.price_types['last']]),
                    'bid': float(res[self.price_types['bid']]),
                    'ask': float(res[self.price_types['ask']])
                }

            return self.prices
        except Exception as e:
            print('get_prices exception:' + self.market + '\n' + str(e) + '\n')
            return None
