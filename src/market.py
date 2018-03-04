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
        self.prices = {}
        self.buy_fee = config['buy_fee']
        self.sell_fee = config['sell_fee']
        self.offline = offline
        self.proxy = {
            'http': 'http://lum-customer-hl_e26add8d-zone-static:h9lsd1exrlcr@zproxy.luminati.io:22225',
            'https': 'http://lum-customer-hl_e26add8d-zone-static:h9lsd1exrlcr@zproxy.luminati.io:22225'
        }

        if self.offline:
            self.__initialize_prices()

    def __initialize_prices(self):
        # client = MongoClient('mongodb://ariel:ariel@ds127536.mlab.com:27536/collector')
        client = MongoClient('mongodb://bitteamisrael:Ariel241096@ds135667-a0.mlab.com:35667,ds135667-a1.mlab.com:35667/bitteamdb?replicaSet=rs-ds135667')
        db = client.bitteamdb
        self.db_data = [x for x in db[self.market.lower()].find({}, {'price': 1, 'bid': 1, 'ask': 1, 'date': 1, '_id': False}).sort("date")]
        self.object_count = db[self.market.lower()].count()
        self.index = 0
        client.close()

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
                res = requests.get(self.api, proxies=self.proxy, timeout=10).json()
                self.prices = {
                    'last': float(res[self.price_types['last']]),
                    'bid': float(res[self.price_types['bid']]),
                    'ask': float(res[self.price_types['ask']])
                }

            return self.prices
        except Exception as e:
            return None
