import json
import os
import time

from src.agent import Agent
from src.ratios_manager import RatiosManager


def log(action, market, price):
    file_name = './log.txt'

    if os.path.exists(file_name):
        mode = 'a'
    else:
        mode = 'w'

    with open(file_name, mode, encoding='UTF-8') as log_file:
        log_file.write(action + ': ' + market.market + ', ' + market.symbol + ' at $' + str(price))


def trade():
    config = json.load(open('./agent_config.json'))
    sampling_time = config['sampling_time']
    ratios_time_length = config['ratios_time_length']

    agent = Agent(config)
    ratio_manager = RatiosManager(sampling_time, ratios_time_length)

    while True:
        source_price = agent.get_market_price('source')
        destination_price = agent.get_market_price('destination')

        if source_price is None or destination_price is None:
            continue

        ratio = source_price / destination_price
        ratio_manager.add_ratio(ratio)

        if agent.can_buy and ratio_manager.average_ratio() - ratio > agent.minimum_ratio_difference:
            log('Buy', agent.source_market, source_price)
        elif not agent.can_buy and ratio_manager.average_ratio() - ratio <= agent.minimum_ratio_difference:
            log('Sell', agent.source_market, source_price)

        time.sleep(ratio_manager.sampling_time)


def main():
    trade()


if __name__ == '__main__':
    main()
