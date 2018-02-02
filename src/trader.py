import time
import random
from datetime import datetime

import pymongo
from pymongo import errors

from .agent import Agent
from .ratios_manager import RatiosManager
from .bit2c import Bit2cClient
from .pbClient import PushbulletClient


class Trader:
    def __init__(self, config, starting_money):
        self.pushbullet = PushbulletClient()
        self.sampling_time = config['sampling_time']
        self.ratios_time_length = config['ratios_time_length']
        self.money = starting_money
        self.coins = 0
        self.order_id = 0
        self.stop_loss_percentage = config['stop_loss_percentage']
        self.offline = config['offline']
        self.agent = Agent(config, self.offline)
        self.ratio_manager = RatiosManager(self.sampling_time, self.ratios_time_length)
        self.client = pymongo.MongoClient(
            'mongodb://bitteamisrael:Ariel241096@ds135667-a0.mlab.com:35667,ds135667-a1.mlab.com:35667/bitteamdb?replicaSet=rs-ds135667')
        self.client.close()
        self.log_initialize()
        self.bid_buy_chance_precentage = 30
        self.did_bid = False
        self.bid_price = 0
        self.bid_fiat_price = 0
        self.bit2Client = Bit2cClient('https://bit2c.co.il',
                                      '340f106f-4e61-4a58-b4f0-9112b5f75b9b',
                                      'A88B7FB7FAC26C8B89A46277FB0E505E21758C43A4E5F02CA6AAC3BC7C5A6B2B')

        if self.offline:
            self.offline_transactions = {  # We are going to use it as a dictionary of documents of offline transactions
                'minimum_buy_ratio_difference': config['minimum_buy_ratio_difference'],
                'minimum_sell_ratio_difference': config['minimum_sell_ratio_difference'],
                'sampling_time': config['sampling_time'],
                'ratios_time_length': config['ratios_time_length'],
                'transactions': []
            }

    def activate(self):
        self.initialize_ratios_list()
        self.trade()

    @staticmethod
    def log_initialize():
        with open('./log.txt', 'w', encoding='UTF-8') as log_file:
            log_file.write('')

    def log_buy(self, market, coins, money, rate):
        current_time = datetime.now()
        message = 'Buy in ' + market.market + ', market ' + market.symbol + ' ' + str(coins) + ' coins for $' +\
            str(money) + ' rate: ' + str(rate) + ' at ' + str(current_time) + '\r\n'

        if not self.offline:
            log = {'method': 'buy', 'market': market.market, 'symbol': market.symbol,
                   'amount:': coins, 'rate': rate, 'money': money, 'timestamp': current_time}
            self.db_safe_insert('online_transactions', log)
            self.pushbullet.push(message, 'Buying crypto')

        with open('./log.txt', 'a', encoding='UTF-8') as log_file:
            log_file.write(message)

    def log_sell(self, market, coins, money, rate):
        current_time = datetime.now()
        message = 'Sell in ' + market.market + ', market ' + market.symbol + ' ' + str(coins) + ' coins for $' +\
            str(money) + ' rate: ' + str(rate) + ' at ' + str(current_time) + '\r\n'

        if not self.offline:
            log = {'method': 'sell', 'market': market.market, 'symbol': market.symbol,
                   'amount:': coins, 'rate': rate, 'money': money, 'timestamp': current_time}
            self.db_safe_insert('online_transactions', log)
            self.pushbullet.push(message, 'Selling crypto')

        with open('./log.txt', 'a', encoding='UTF-8') as log_file:
            log_file.write(message)
    
    def log_bid(self, market, coins, money, bid_rate):
        current_time = datetime.now()
        message = 'Bid in ' + market.market + ', market ' + market.symbol + ' ' + str(coins) + ' coins for $' +\
            str(money) + ' rate: ' + str(bid_rate) + ' at ' + str(current_time) + '\r\n'

        if not self.offline:
            log = {'method': 'bid', 'market': market.market, 'symbol': market.symbol,
                   'amount:': coins, 'rate': bid_rate, 'money': money, 'timestamp': current_time}
            self.db_safe_insert('online_transactions', log)
            self.pushbullet.push(message, 'Biding crypto')

        with open('./log.txt', 'a', encoding='UTF-8') as log_file:
            log_file.write(message)
    
    def log_remove_bid(self, market, bid_rate):
        current_time = datetime.now()
        message = 'Remove bid in ' + market.market + ', market ' + market.symbol + ' rate: ' + \
        str(bid_rate) + ' at ' + str(current_time) + '\r\n'

        if not self.offline:
            log = {'method': 'removeBid', 'market': market.market, 'symbol': market.symbol,
                   'rate': bid_rate, 'timestamp': current_time}
            self.db_safe_insert('online_transactions', log)
            self.pushbullet.push(message, 'Remove crypto')

        with open('./log.txt', 'a', encoding='UTF-8') as log_file:
            log_file.write(message)

    @staticmethod
    def log_error(error):
        with open('./log.txt', 'a', encoding='UTF-8') as log_file:
            log_file.write(
                'Error: ' + error + ' At ' + str(datetime.now()) + '\r\n')

    def initialize_ratios_list(self):
        if not self.offline:
            bit2c_docs = [x['bid'] / self.agent.fiat_rate for x in
                          self.client.bitteamdb['bit2c'].find({}, {'bid': 1, '_id': False})
                              .sort([('date', pymongo.DESCENDING)]).limit(self.ratio_manager.list_length)]
            bitfinex_docs = [x['bid'] for x in
                             self.client.bitteamdb['bitfinex'].find({}, {'bid': 1, '_id': False})
                                 .sort([('date', pymongo.DESCENDING)]).limit(self.ratio_manager.list_length)]
            self.client.close()
            ratios = []

            for i in range(len(bit2c_docs)):
                ratios.append(bit2c_docs[i] / bitfinex_docs[i])

            self.ratio_manager.ratios = ratios

        while not self.ratio_manager.is_list_full():
            self.check_ratio(True)
            time.sleep(self.ratio_manager.sampling_time)

    def trade(self):
        if self.offline:
            for x in range(self.agent.samples_count):
                self.check_ratio()

            self.db_safe_insert('offline_transactions', self.offline_transactions)
        else:
            while True:
                self.check_ratio()
                time.sleep(self.ratio_manager.sampling_time)

    def check_ratio(self, initialization=False):
        source_prices = self.agent.get_market_prices('source')
        destination_prices = self.agent.get_market_prices('destination')

        # minimum_ratio_difference = self.calc_min_ratio_diff(source_prices, destination_prices)

        if source_prices is not None and destination_prices is not None:
            ratio = source_prices['bid'] / destination_prices['bid']
            self.ratio_manager.add_ratio(ratio)

            if not initialization:
                future_price = self.ratio_manager.average_ratio() * destination_prices['bid']

                if self.agent.can_buy and \
                        self.ratio_manager.average_ratio() - ratio > self.agent.minimum_buy_ratio_difference and \
                        future_price - source_prices['bid'] > 100: 
                    if not self.did_bid:
                        self.bid_fiat_price = self.agent.source_market.prices['bid'] + 1
                        self.bid_price = self.bid_fiat_price / self.agent.fiat_rate
                        self.bid(self.money / self.bid_price, self.bid_fiat_price)
                        self.log_bid(self.agent.source_market, self.coins, self.money / self.bid_price, self.bid_price)
                    elif self.agent.source_market.prices['bid'] > self.bid_fiat_price:
                        self.bid_fiat_price = self.agent.source_market.prices['bid'] + 1
                        self.bid_price = self.bid_fiat_price / self.agent.fiat_rate
                        self.remove_bid()
                        self.bid(self.money / self.bid_price, self.bid_fiat_price)

                    if self.did_bid and self.did_buy_from_bid():
                        money = self.money
                        self.coins = self.money / self.bid_price * 0.995
                        self.money = 0
                        self.agent.can_buy = False
                        self.did_bid = False
                        self.log_buy(self.agent.source_market, self.coins, money, self.bid_price)

                        if self.offline:
                            self.offline_transactions['transactions'].append({'buy': {
                                'price': self.bid_price,
                                'bid': source_prices['bid'],
                                'ask': source_prices['ask'],
                                'volume': 0,
                                'date': source_prices['date'],
                                'ratio': self.ratio_manager.average_ratio()
                            }})
                elif not self.agent.can_buy and \
                        (self.ratio_manager.average_ratio() - ratio <= self.agent.minimum_sell_ratio_difference or
                         self.stop_loss(source_prices['bid'])):
                    if self.sell(self.coins):
                        coins = self.coins
                        self.money = self.coins * source_prices['bid'] * 0.995
                        self.coins = 0
                        self.agent.can_buy = True
                        self.log_sell(self.agent.source_market, coins, self.money, source_prices['bid'])

                        if self.offline:
                            self.offline_transactions['transactions'][-1]['sell'] = {
                                'price': source_prices['bid'],
                                'bid': source_prices['bid'],
                                'ask': source_prices['ask'],
                                'volume': 0,
                                'date': source_prices['date'],
                                'ratio': self.ratio_manager.average_ratio()
                            }
                            self.offline_transactions['transactions'][-1]['money'] = self.money
                elif self.did_bid:
                    self.remove_bid()
                    self.log_remove_bid(self.agent.source_market, self.bid_price)

    def bid(self, amount, price):
        if self.offline:
            self.did_bid = True
        else:
            res = self.bit2Client.add_order({'Amount': amount, 'Price': price, 'IsBid': True})

            if res['OrderResponse']['HasError']:
                self.log_error(res['OrderResponse']['Error'])
            else:
                self.order_id = res['NewOrder']['id']
                self.did_bid = True

    def sell(self, amount):
        if not self.offline:
            res = self.bit2Client.sell_order(amount)

            if res['OrderResponse']['HasError']:
                self.log_error(res['OrderResponse']['Error'])
                return False
            else:
                return True

    def remove_bid(self):
        if self.offline:
            self.did_bid = False
        else:
            res = self.bit2Client.cancel_order(self.order_id)

            if res['OrderResponse']['HasError']:
                self.log_error(res['OrderResponse']['Error'])
            else:
                self.did_bid = False

    def did_buy_from_bid(self):
        if self.offline:
            return random.randint(0, 100) < self.bid_buy_chance_precentage
        else:
            res = self.bit2Client.get_order(self.order_id)

            if 'Error' in res:
                if res['Error'] == 'No order found.':
                    return True
            if 'status' not in res:
                print(res)
            return res['status'] != 'Open'

    def stop_loss(self, current_bid):
        change_percentage = ((float(current_bid) - self.bid_price) / self.bid_price) * 100
        if change_percentage > self.stop_loss_percentage:
            return True
        else:
            return False

    def db_safe_insert(self, collection, document):
        for i in range(5):
            try:
                self.client.bitteamdb[collection].insert_one(document)
                self.client.close()
                break
            except pymongo.errors.AutoReconnect:
                self.log_error(str(datetime.utcnow()) + ' AutoReconnect')

                time.sleep(pow(2, i))

    @staticmethod
    def calc_min_ratio_diff(source_prices, destination_prices):
        source_ask_price = source_prices['ask']
        source_bid_price = source_prices['bid']
        source_last_price = source_prices['last']
        destination_last_price = destination_prices['last']
        source_ask_bid_margin = source_ask_price - source_bid_price
        regular_ratio = destination_last_price / source_last_price
        # fees are supposed to be calculated as the following:
        # amount of money we are going to buy with * 0.005(0.5% commission)
        # +
        # amount of money we are going to get after sell * 0.005(0.5% commission)
        # For now i used 65 which stands for:
        # 20000 * 0.005 = 100
        # 25000 * 0.005 = 125 (Assuming we gained 25$ on the deal)
        # 225 / USDILS rate(3.51) = 64.10256...(ceiling)
        fees = 65
        profitable_ratio = (destination_last_price + source_ask_bid_margin + fees) / source_last_price
        min_ratio = profitable_ratio - regular_ratio

        return min_ratio
