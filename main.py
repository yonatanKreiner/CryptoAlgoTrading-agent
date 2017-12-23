import json
from src.trader import Trader


def main():
    config = json.load(open('src/agent_config.json'))
    trader = Trader(config)
    trader.activate()

    if trader.offline:
        print(trader.profit)


if __name__ == '__main__':
    main()
