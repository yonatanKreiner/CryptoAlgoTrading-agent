import time
import json
from .agent import Agent, OfflineAgent
from .ratios_manager import RatiosManager


def activate():
    config = json.load(open('src/agent_config.json'))
    sampling_time = config['sampling_time']
    ratios_time_length = config['ratios_time_length']

    agent = Agent(config)
    ratio_manager = RatiosManager(sampling_time, ratios_time_length)

    initialize_ratios_list(agent, ratio_manager)
    trade(agent, ratio_manager)


def activate_offline():
    config = json.load(open('src/agent_config.json'))
    sampling_time = config['sampling_time']
    ratios_time_length = config['ratios_time_length']

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
            offline_check_ratio(agent, ratio_manager, index)
            index += 1
        else:
            check_ratio(agent, ratio_manager)


def trade(agent, ratio_manager):
    while True:
        check_ratio(agent, ratio_manager, True)


def check_ratio(agent, ratio_manager, ready=False):
    source_price = agent.get_market_price('source')
    destination_price = agent.get_market_price('destination')

    if source_price is not None and destination_price is not None:
        ratio = source_price / destination_price
        ratio_manager.add_ratio(ratio)

        if ready and agent.can_buy and ratio_manager.average_ratio() - ratio > agent.minimum_ratio_difference:
            log('Buy', agent.source_market, source_price)
            agent.can_buy = False
        elif ready and not agent.can_buy and ratio_manager.average_ratio() - ratio <= agent.minimum_ratio_difference:
            log('Sell', agent.source_market, source_price)
            agent.can_buy = True

        print('avarage: ' + str(ratio_manager.average_ratio()) + ', current: ' + str(ratio) + ', difference: ' + str(ratio_manager.average_ratio() - ratio))
        time.sleep(ratio_manager.sampling_time)


def offline_trade(agent, ratio_manager, object_count):
    index = ratio_manager.list_length

    while index < object_count:
        offline_check_ratio(agent, ratio_manager, index, True)
        index += 1


def offline_check_ratio(agent, ratio_manager, index, ready=False):
    source_price = agent.get_market_price('source', index)
    destination_price = agent.get_market_price('destination', index)

    if source_price is not None and destination_price is not None:
        ratio = source_price / destination_price
        ratio_manager.add_ratio(ratio)

        if ready and agent.can_buy and ratio_manager.average_ratio() - ratio > agent.minimum_ratio_difference:
            log('Buy', agent.source_market, source_price)
            agent.can_buy = False
        elif ready and not agent.can_buy and ratio_manager.average_ratio() - ratio <= agent.minimum_ratio_difference:
            log('Sell', agent.source_market, source_price)
            agent.can_buy = True
