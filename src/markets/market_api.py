import random

from .bit2c import Bit2cClient
from ..utils.logger import Logger


class MarketAPI:
    def __init__(self, db, config):
        self.offline = config['offline']
        self.did_bid = False
        self.logger = Logger(db, config)
        self.client = Bit2cClient('https://bit2c.co.il',
            '340f106f-4e61-4a58-b4f0-9112b5f75b9b',
            'A88B7FB7FAC26C8B89A46277FB0E505E21758C43A4E5F02CA6AAC3BC7C5A6B2B')
        
        if self.offline:
            self.bid_buy_chance_precentage = 30
    
    def bid(self, amount, price, did_bid):
        if self.offline:
            return True
        else:
            res = self.client.add_order({'Amount': amount, 'Price': price, 'IsBid': True})

            if res['OrderResponse']['HasError']:
                self.logger.log_error(res['OrderResponse']['Error'])
                return did_bid
            else:
                self.order_id = res['NewOrder']['id']
                return True
    
    def remove_bid(self, did_bid):
        if self.offline:
            return False
        else:
            res = self.client.cancel_order(self.order_id)

            if res['OrderResponse']['HasError']:
                self.logger.log_error(res['OrderResponse']['Error'])
                return did_bid
            else:
                return False

    def did_buy_from_bid(self):
        if self.offline:
            return random.randint(0, 100) < self.bid_buy_chance_precentage
        else:
            res = self.client.get_order(self.order_id)

            if 'Error' in res:
                if res['Error'] == 'No order found.':
                    return True
            if 'status' not in res:
                print(res)
            return res['status'] != 'Open'
    
    def sell(self, amount):
        if self.offline:
            return True
        else:
            res = self.client.sell_order(amount)

            if res['OrderResponse']['HasError']:
                self.logger.log_error(res['OrderResponse']['Error'])
                return False
            else:
                return True
