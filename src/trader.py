import time
from datetime import datetime
from .agent import Agent
from .ratios_manager import RatiosManager


class Trader:
    def __init__(self, config):
        self.sampling_time = config['sampling_time']
        self.ratios_time_length = config['ratios_time_length']
        self.profit = 0
        self.offline = config['offline']
        self.agent = Agent(config, self.offline)
        self.ratio_manager = RatiosManager(self.sampling_time, self.ratios_time_length)

    def activate(self):
        self.initialize_ratios_list()
        self.trade()

    @staticmethod
    def log(action, market, price):
        with open('./log.txt', 'a', encoding='UTF-8') as log_file:
            log_file.write(action + ': ' + market.market + ', ' + market.symbol + ' $' + str(price) + ' at ' +
                           str(datetime.now()) + '\r\n')

    def initialize_ratios_list(self):
        while not self.ratio_manager.is_list_full():
            self.check_ratio(True)

    def trade(self):
        if self.offline:
            for x in range(self.agent.samples_count):
                self.check_ratio()
        else:
            while True:
                self.check_ratio()
                time.sleep(self.ratio_manager.sampling_time)

    def check_ratio(self, initialization=False):
        try:
            source_prices = self.agent.get_market_prices('source')
            destination_prices = self.agent.get_market_prices('destination')

            #minimum_ratio_difference = self.calc_min_ratio_diff(source_prices, destination_prices)

            if source_prices['last'] is not None and destination_prices['last'] is not None:
                ratio = source_prices['last'] / destination_prices['last']
                self.ratio_manager.add_ratio(ratio)

                if not initialization:
                    if self.agent.can_buy and \
                            self.ratio_manager.average_ratio() - ratio > self.agent.minimum_buy_ratio_difference:
                        self.log('Buy', self.agent.source_market, source_prices['ask'])
                        self.agent.can_buy = False
                        self.profit -= source_prices['ask']
                    elif not self.agent.can_buy and \
                            self.ratio_manager.average_ratio() - ratio <= self.agent.minimum_sell_ratio_difference:
                        self.log('Sell', self.agent.source_market, source_prices['bid'])
                        self.agent.can_buy = True
                        self.profit += source_prices['bid']
        except:
            pass

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
