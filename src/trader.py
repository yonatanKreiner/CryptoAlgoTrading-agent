import time
from datetime import datetime
from .agent import Agent
from .ratios_manager import RatiosManager
from pymongo import MongoClient


class Trader:
    def __init__(self, config, starting_money):
        self.sampling_time = config['sampling_time']
        self.ratios_time_length = config['ratios_time_length']
        self.money = starting_money
        self.coins = 0
        self.offline = config['offline']
        self.agent = Agent(config, self.offline)
        self.ratio_manager = RatiosManager(self.sampling_time, self.ratios_time_length)
        self.offline_transactions = { # We are going to use it as a dictionary of documents of offline transactions
            'minimum_buy_ratio_difference': config['minimum_buy_ratio_difference'],
            'minimum_sell_ratio_difference': config['minimum_sell_ratio_difference'],
            'sampling_time': config['sampling_time'],
            'ratios_time_length': config['ratios_time_length'],
            'transactions': []
        }
        self.client = MongoClient('mongodb://ariel:ariel@ds127536.mlab.com:27536/collector')
        self.db = self.client.collector

    def activate(self):
        self.initialize_ratios_list()
        self.trade()

    @staticmethod
    def log_buy(market, coins, money, rate):
        with open('./log.txt', 'a', encoding='UTF-8') as log_file:
            log_file.write('Buy in ' + market.market + ', market ' + market.symbol + ' ' + str(coins) + ' coins for $' +
                           str(money) + ' rate: ' + str(rate) + ' at ' + str(datetime.now()) + '\r\n')

    @staticmethod
    def log_sell(market, coins, money, rate):
        with open('./log.txt', 'a', encoding='UTF-8') as log_file:
            log_file.write('Sell in ' + market.market + ', market ' + market.symbol + ' ' + str(coins) + ' coins for $' +
                           str(money) + ' rate: ' + str(rate) + ' at ' + str(datetime.now()) + '\r\n')

    def initialize_ratios_list(self):
        while not self.ratio_manager.is_list_full():
            self.check_ratio(True)

    def trade(self):
        if self.offline:
            for x in range(self.agent.samples_count):
                self.check_ratio()

            self.db['offline_transactions'].insert_one(self.offline_transactions)
        else:
            while True:
                self.check_ratio()
                time.sleep(self.ratio_manager.sampling_time)

    def check_ratio(self, initialization=False):
        try:
            source_prices = self.agent.get_market_prices('source')
            destination_prices = self.agent.get_market_prices('destination')

            minimum_ratio_difference = self.calc_min_ratio_diff(source_prices, destination_prices)

            if source_prices['last'] is not None and destination_prices['last'] is not None:
                ratio = source_prices['ask'] / destination_prices['ask']
                self.ratio_manager.add_ratio(ratio)

                if not initialization:
                    if self.agent.can_buy and \
                            self.ratio_manager.average_ratio() - ratio > self.agent.minimum_buy_ratio_difference:
                        money = self.money
                        self.coins = self.money / source_prices['ask']
                        self.money = 0
                        self.agent.can_buy = False
                        self.log_buy(self.agent.source_market, self.coins, money, source_prices['ask'])
                        self.offline_transactions['transactions'].append({'buy': {
                            'price': source_prices['ask'],
                            'bid': source_prices['bid'],
                            'ask': source_prices['ask'],
                            'volume': 0,
                            'date': source_prices['date']
                        }})
                    elif not self.agent.can_buy and \
                            self.ratio_manager.average_ratio() - ratio <= self.agent.minimum_sell_ratio_difference:
                        coins = self.coins
                        self.money = self.coins * source_prices['bid']
                        self.coins = 0
                        self.agent.can_buy = True
                        self.log_sell(self.agent.source_market, coins, self.money, source_prices['bid'])
                        self.offline_transactions['transactions'][-1]['sell'] = {
                            'price': source_prices['bid'],
                            'bid': source_prices['bid'],
                            'ask': source_prices['ask'],
                            'volume': 0,
                            'date': source_prices['date']
                        }
                        self.offline_transactions['transactions'][-1]['money'] = self.money
        except Exception as e:
            print(str(e))

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
