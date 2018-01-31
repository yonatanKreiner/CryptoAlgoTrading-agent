import json
from src.trader import Trader


def main(starting_money):
    config = json.load(open('src/agent_config.json'))
    trader = Trader(config, starting_money)
    trader.activate()

    if trader.offline:
        print('money: ' + str(trader.money))
        print('profit: ' + str(trader.money - starting_money))


if __name__ == '__main__':
    main(5)
