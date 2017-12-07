import json
import time
from agent import Agent
from ratios_manager import RatiosManager


def buy(market, price):
    with open('./log.txt', 'w+', encoding='UTF-8') as log_file:
        log_file.write('buying from ' + market.market + ', ' + market.symbol + ' at $' + price)


def sell(market, price):
    with open('./log.txt', 'w+', encoding='UTF-8') as log_file:
        log_file.write('selling to ' + market.market + ', ' + market.symbol + ' at $' + price)


def trade():
    config = json.load(open('./agent_config.json'))
    sampling_time = config['sampling_time']
    ratios_time_length = config['ratios_time_length']

    agent = Agent(config)
    ratio_manager = RatiosManager(sampling_time, ratios_time_length)

    while True:
        source_price = agent.get_market_price('source')
        destination_price = agent.get_market_price('destination')
        ratio = source_price / destination_price
        ratio_manager.add_ratio(ratio)

        if agent.can_buy and ratio - ratio_manager.average_ratio() > agent.minimum_ratio_difference:
            buy(agent.source_market, source_price)
        elif not agent.can_buy and ratio - ratio_manager.average_ratio() <= agent.minimum_ratio_difference:
            sell(agent.source_market, source_price)

        time.sleep(ratio_manager.sampling_time)


def main():
    trade()


if __name__ == '__main__':
    main()
