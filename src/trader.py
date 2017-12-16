import time
import json
from .agent import Agent
from .ratios_manager import RatiosManager
from datetime import datetime


def activate():
    config = json.load(open('src/agent_config.json'))
    sampling_time = config['sampling_time']
    ratios_time_length = config['ratios_time_length']

    agent = Agent(config)
    ratio_manager = RatiosManager(sampling_time, ratios_time_length)

    initialize_ratios_list(agent, ratio_manager)
    trade(agent, ratio_manager)


def log(action, market, price):
    with open('./log.txt', 'a', encoding='UTF-8') as log_file:
        log_file.write(action + ': ' + market.market + ', ' + market.symbol + ' at $' + str(price) + '\r\n')


def initialize_ratios_list(agent, ratio_manager):
    while not ratio_manager.is_list_full():
        source_price = agent.get_market_price('source')
        destination_price = agent.get_market_price('destination')

        if source_price is not None and destination_price is not None:
            ratio = source_price / destination_price
            ratio_manager.add_ratio(ratio)

def calc_min_ratio_diff(agent):
    ask_price = agent.get_market_price('source', 'ask')
    bid_price = agent.get_market_price('source', 'bid')
    ask_bid_margin = ask - bid

def trade(agent, ratio_manager):
    profit = 0
    buy_time = None

    while True:
        source_price = agent.get_market_price('source', 'last')
        destination_price = agent.get_market_price('destination', 'last')

        if source_price is not None and destination_price is not None:
            ratio = source_price / destination_price
            ratio_manager.add_ratio(ratio)

            if agent.can_buy and ratio_manager.average_ratio() - ratio > agent.minimum_ratio_difference:
                log('Buy', agent.source_market, source_price)
                buy_time = datetime.now()
                agent.can_buy = False
                profit -= source_price
                print('average: ' + str(ratio_manager.average_ratio()) + ', current: ' + str(ratio) + ', difference: ' + str(ratio_manager.average_ratio() - ratio))
            elif not agent.can_buy and ratio_manager.average_ratio() - ratio <= agent.minimum_ratio_difference:
                log('Sell', agent.source_market, source_price)
                sell_time = datetime.now()
                agent.can_buy = True
                profit += source_price
                print('average: ' + str(ratio_manager.average_ratio()) + ', current: ' + str(ratio) + ', difference: ' + str(ratio_manager.average_ratio() - ratio) + ', profit:' + str(profit) + ', timestamp:(hh:mm:ss.ms) {}'.format(sell_time - buy_time))

            time.sleep(ratio_manager.sampling_time)