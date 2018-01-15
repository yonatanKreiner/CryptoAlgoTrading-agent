import time
import random
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
        self.buy_price = 0
        self.stop_loss_precentage = config['stop_loss_precentage']
        self.offline = config['offline']
        self.agent = Agent(config, self.offline)
        self.ratio_manager = RatiosManager(self.sampling_time, self.ratios_time_length)
        self.offline_transactions = {  # We are going to use it as a dictionary of documents of offline transactions
            'minimum_buy_ratio_difference': config['minimum_buy_ratio_difference'],
            'minimum_sell_ratio_difference': config['minimum_sell_ratio_difference'],
            'sampling_time': config['sampling_time'],
            'ratios_time_length': config['ratios_time_length'],
            'transactions': []
        }
        client = MongoClient('mongodb://bitteamisrael:Ariel241096@ds135667-a0.mlab.com:35667,ds135667-a1.mlab.com:35667/bitteamdb?replicaSet=rs-ds135667')
        self.db = client.bitteamdb
        self.log_initialize()
        self.bid_buy_chance_precentage = 30
        self.did_bid = False

    def activate(self):
        self.initialize_ratios_list()
        self.trade()

    @staticmethod
    def log_initialize():
        with open('./log.txt', 'w', encoding='UTF-8') as log_file:
            log_file.write('')

    @staticmethod
    def log_buy(market, coins, money, rate):
        with open('./log.txt', 'a', encoding='UTF-8') as log_file:
            log_file.write('Buy in ' + market.market + ', market ' + market.symbol + ' ' + str(coins) + ' coins for $' +
                           str(money) + ' rate: ' + str(rate) + ' at ' + str(datetime.now()) + '\r\n')

    @staticmethod
    def log_sell(market, coins, money, rate):
        with open('./log.txt', 'a', encoding='UTF-8') as log_file:
            log_file.write(
                'Sell in ' + market.market + ', market ' + market.symbol + ' ' + str(coins) + ' coins for $' +
                str(money) + ' rate: ' + str(rate) + ' at ' + str(datetime.now()) + '\r\n')

    def did_buy_from_bid(self):
        return random.randint(0, 100) < self.bid_buy_chance_precentage

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
                        self.bid()
                    else:
                        self.update_bid()
                    
                    if self.did_buy_from_bid():
                        money = self.money
                        self.coins = self.money / source_prices['bid']
                        self.money = 0
                        self.agent.can_buy = False
                        self.buy_price = source_prices['bid']
                        self.log_buy(self.agent.source_market, self.coins, money, source_prices['ask'])
                        self.offline_transactions['transactions'].append({'buy': {
                            'price': source_prices['ask'],
                            'bid': source_prices['bid'],
                            'ask': source_prices['ask'],
                            'volume': 0,
                            'date': source_prices['date'],
                            'ratio': self.ratio_manager.average_ratio()
                        }})
                elif not self.agent.can_buy and \
                        (self.ratio_manager.average_ratio() - ratio <= self.agent.minimum_sell_ratio_difference or \
                        self.stop_loss(source_prices['bid'])):
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
                        'date': source_prices['date'],
                        'ratio': self.ratio_manager.average_ratio()
                    }
                    self.offline_transactions['transactions'][-1]['money'] = self.money
                else:
                    self.remove_bid()
    
    def bid(self):
        self.did_bid = True
    
    def update_bid(self):
        pass
    
    def remove_bid(self):
        self.did_bid = False
        
    def stop_loss(self, current_bid):
        change_percentage = ((float(current_bid) - self.buy_price) / self.buy_price) * 100
        if change_percentage > self.stop_loss_precentage:
            return True
        else:
            return False

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
