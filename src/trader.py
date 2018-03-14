import time
import random
from datetime import datetime

from .agent import Agent
from .ratios_manager import RatiosManager
from .markets.bit2c import Bit2cClient
from .utils.logger import Logger
from .utils.DB import DB
from .utils.currency_converter import CurrencyConverter
from .markets.market_api import MarketAPI

class Trader:
    def __init__(self, config, starting_money):
        self.offline = config['offline']
        self.db = DB(config)
        self.currency_converter = CurrencyConverter(config)
        self.logger = Logger(config, self.db)
        self.sampling_time = config['sampling_time']
        self.ratios_time_length = config['ratios_time_length']
        self.money = starting_money
        self.coins = 0
        self.order_id = 0
        self.stop_loss_percentage = config['stop_loss_percentage']
        self.agent = Agent(config, self.db, self.currency_converter, self.offline)
        self.ratio_manager = RatiosManager(self.sampling_time, self.ratios_time_length)
        self.did_bid = False
        self.bid_price = 0
        self.bid_fiat_price = 0
        self.market_api = MarketAPI(self.db, self.logger, config)

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

    def initialize_ratios_list(self):
        if not self.offline:
            bit2c_docs = [x['bid'] / self.currency_converter.fiat_rate for x in self.db.get_tickers(self.agent.source_market.market.lower(), limit=self.ratio_manager.list_length)]
            bitfinex_docs = [x['bid'] for x in self.db.get_tickers(self.agent.destination_market.market.lower(), limit=self.ratio_manager.list_length)]
            ratios = []

            for i in range(len(bit2c_docs)):
                ratios.append(bit2c_docs[i] / bitfinex_docs[i])

            self.ratio_manager.ratios = ratios

        while not self.ratio_manager.is_list_full():
            self.check_ratio(True)
            if not self.offline:
                time.sleep(self.ratio_manager.sampling_time)

    def trade(self):
        if self.offline:
            for x in range(self.agent.samples_count - self.ratio_manager.list_length):
                self.check_ratio()

            self.db.db_safe_insert('offline_transactions', self.offline_transactions)
        else:
            while True:
                self.check_ratio()
                self.currency_converter.update_fiat_rate()
                time.sleep(self.ratio_manager.sampling_time)

    def check_ratio(self, initialization=False):
        source_prices = self.agent.get_market_prices('source')
        destination_prices = self.agent.get_market_prices('destination')

        if source_prices is not None and destination_prices is not None:
            ratio = source_prices['bid'] / destination_prices['bid']
            self.ratio_manager.add_ratio(ratio)

            if not initialization:
                if self.agent.can_buy and \
                        self.ratio_manager.average_ratio() - ratio > self.agent.minimum_buy_ratio_difference:
                    if not self.did_bid:
                        self.bid_fiat_price = self.agent.source_market.prices['bid'] + 1
                        self.bid_price = self.bid_fiat_price / self.currency_converter.fiat_rate
                        self.did_bid = self.market_api.bid(self.money / self.bid_price, self.bid_fiat_price, self.did_bid)

                        self.logger.log_bid(self.agent.source_market, self.coins, self.money / self.bid_price, self.bid_price)
                    elif self.agent.source_market.prices['bid'] > self.bid_fiat_price:
                        self.bid_fiat_price = self.agent.source_market.prices['bid'] + 1
                        self.bid_price = self.bid_fiat_price / self.currency_converter.fiat_rate
                        self.did_bid = self.market_api.remove_bid(self.did_bid)
                        self.did_bid = self.market_api.bid(self.money / self.bid_price, self.bid_fiat_price, self.did_bid)

                    if self.did_bid and self.market_api.did_buy_from_bid():
                        money = self.money

                        if self.offline:
                            self.coins = self.money / self.bid_price * 0.995
                        else:
                            self.coins = self.market_api.get_balance()                            

                        self.money = 0
                        self.agent.can_buy = False
                        self.did_bid = False
                        self.logger.log_buy(self.agent.source_market, self.coins, money, self.bid_price)

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
                    if self.market_api.sell(self.coins):
                        coins = self.coins
                        self.money = self.coins * source_prices['bid'] * 0.995
                        self.coins = 0
                        self.agent.can_buy = True
                        self.logger.log_sell(self.agent.source_market, coins, self.money, source_prices['bid'])

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
                    self.did_bid = self.market_api.remove_bid(self.did_bid)
                    self.logger.log_remove_bid(self.agent.source_market, self.bid_price)

    def stop_loss(self, current_bid):
        change_percentage = ((float(current_bid) - self.bid_price) / self.bid_price) * 100

        return change_percentage <= -self.stop_loss_percentage
