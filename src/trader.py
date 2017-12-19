import time
import json
from .agent import Agent, OfflineAgent
from .ratios_manager import RatiosManager
from datetime import datetime


config = json.load(open('src/agent_config.json'))
sampling_time = config['sampling_time']
ratios_time_length = config['ratios_time_length']


def activate():
    agent = Agent(config)
    ratio_manager = RatiosManager(sampling_time, ratios_time_length)

    initialize_ratios_list(agent, ratio_manager)
    trade(agent, ratio_manager)


def activate_offline():
    agent = OfflineAgent(config)
    ratio_manager = RatiosManager(sampling_time, ratios_time_length)

    initialize_ratios_list(agent, ratio_manager, True)
    offline_trade(agent, ratio_manager, agent.object_count)


def log(action, market, price):
    with open('./log.txt', 'a', encoding='UTF-8') as log_file:
        log_file.write(action + ': ' + market.market + ', ' + market.symbol + ' at $' + str(price) + '\r\n')


def initialize_ratios_list(agent, ratio_manager, offline=False):
    index = 0

    while not ratio_manager.is_list_full():
        if offline:
            source_price = agent.get_market_price('source', index)
            destination_price = agent.get_market_price('destination', index)
            index += 1
        else:
            source_price = agent.get_market_price('source')
            destination_price = agent.get_market_price('destination')

        if source_price is not None and destination_price is not None:
            ratio = source_price / destination_price
            ratio_manager.add_ratio(ratio)


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


def trade(agent, ratio_manager):
    profit = 0
    buy_time = None

    while True:
        agent.update_fiat_rate()

        source_prices = agent.get_market_prices('source')
        destination_prices = agent.get_market_prices('destination')

        minimum_ratio_difference = calc_min_ratio_diff(source_prices, destination_prices)

        if source_prices['last'] is not None and destination_prices['last'] is not None:
            ratio = source_prices['last'] / destination_prices['last']
            ratio_manager.add_ratio(ratio)

            if agent.can_buy and ratio_manager.average_ratio() - ratio > minimum_ratio_difference:
                log('Buy', agent.source_market, source_prices['ask'])
                buy_time = datetime.now()
                agent.can_buy = False
                profit -= source_prices['ask']
                print('average: ' + str(ratio_manager.average_ratio()) + ', current: ' + str(ratio) + ', difference: ' + str(ratio_manager.average_ratio() - ratio))
            elif not agent.can_buy and ratio_manager.average_ratio() - ratio <= minimum_ratio_difference:
                log('Sell', agent.source_market, source_prices['bid'])
                sell_time = datetime.now()
                agent.can_buy = True
                profit += source_prices['bid']
                print('average: ' + str(ratio_manager.average_ratio()) + ', current: ' + str(ratio) + ', difference: ' + str(ratio_manager.average_ratio() - ratio) + ', profit:' + str(profit) + ', timestamp:(hh:mm:ss.ms) {}'.format(sell_time - buy_time))

            time.sleep(ratio_manager.sampling_time)


def offline_trade(agent, ratio_manager, object_count):
    profit = 0
    index = int(ratio_manager.list_length)

    while index < object_count:
        source_price = agent.get_market_price('source', index)
        destination_price = agent.get_market_price('destination', index)

        if source_price is not None and destination_price is not None:
            ratio = source_price / destination_price
            ratio_manager.add_ratio(ratio)

            if agent.can_buy and ratio_manager.average_ratio() - ratio > agent.minimum_ratio_difference:
                agent.can_buy = False
                profit -= source_price
            elif not agent.can_buy and ratio_manager.average_ratio() - ratio <= agent.minimum_ratio_difference:
                agent.can_buy = True
                profit += source_price
        index += 1

    print('profit: ' + str(profit))
