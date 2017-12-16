from .market import Market, OfflineMarket


class Agent:
    def __init__(self, config):
        self.can_buy = True
        self.source_market = Market(config['source'])
        self.destination_market = Market(config['destination'])

        self.minimum_ratio_difference = config['minimum_ratio_difference']

    def get_market_price(self, market):
        if market == 'source':
            return self.source_market.get_price()
        else:
            return self.destination_market.get_price()


class OfflineAgent:
    def __init__(self, config):
        self.can_buy = True
        self.source_market = OfflineMarket(config['source'])
        self.destination_market = OfflineMarket(config['destination'])
        self.object_count = min((self.source_market.object_count, self.destination_market.object_count))

        self.minimum_ratio_difference = config['minimum_ratio_difference']

    def get_market_price(self, market, index):
        if market == 'source':
            return self.source_market.get_offline_price(index)
        else:
            return self.destination_market.get_offline_price(index)
