from datetime import datetime
from .pushbullet_client import PushbulletClient
from .DB import DB

class Logger:
    def __init__(self, config):
        self.offline = config['offline']
        self.pushbullet = PushbulletClient()
        self.db = DB(config)
        self.log_initialize()

    @staticmethod
    def log_initialize():
        with open('./log.txt', 'w', encoding='UTF-8') as log_file:
            log_file.write('')

    def log_buy(self, market, coins, money, rate):
        current_time = datetime.now()
        message = 'Buy in ' + market.market + ', market ' + market.symbol + ' ' + str(coins) + ' coins for $' +\
            str(money) + ' rate: ' + str(rate) + ' at ' + str(current_time) + '\r\n'

        if not self.offline:
            log = {'method': 'buy', 'market': market.market, 'symbol': market.symbol,
                   'amount:': coins, 'rate': rate, 'money': money, 'timestamp': current_time}
            self.db.db_safe_insert('online_transactions', log)
            self.pushbullet.push(message, 'Buying crypto')

        with open('./log.txt', 'a', encoding='UTF-8') as log_file:
            log_file.write(message)

    def log_sell(self, market, coins, money, rate):
        current_time = datetime.now()
        message = 'Sell in ' + market.market + ', market ' + market.symbol + ' ' + str(coins) + ' coins for $' +\
            str(money) + ' rate: ' + str(rate) + ' at ' + str(current_time) + '\r\n'

        if not self.offline:
            log = {'method': 'sell', 'market': market.market, 'symbol': market.symbol,
                   'amount:': coins, 'rate': rate, 'money': money, 'timestamp': current_time}
            self.db.db_safe_insert('online_transactions', log)
            self.pushbullet.push(message, 'Selling crypto')

        with open('./log.txt', 'a', encoding='UTF-8') as log_file:
            log_file.write(message)
    
    def log_bid(self, market, coins, money, bid_rate):
        current_time = datetime.now()
        message = 'Bid in ' + market.market + ', market ' + market.symbol + ' ' + str(coins) + ' coins for $' +\
            str(money) + ' rate: ' + str(bid_rate) + ' at ' + str(current_time) + '\r\n'

        if not self.offline:
            log = {'method': 'bid', 'market': market.market, 'symbol': market.symbol,
                   'amount:': coins, 'rate': bid_rate, 'money': money, 'timestamp': current_time}
            self.db.db_safe_insert('online_transactions', log)
            #self.pushbullet.push(message, 'Biding crypto')

        with open('./log.txt', 'a', encoding='UTF-8') as log_file:
            log_file.write(message)
    
    def log_remove_bid(self, market, bid_rate):
        current_time = datetime.now()
        message = 'Remove bid in ' + market.market + ', market ' + market.symbol + ' rate: ' + \
        str(bid_rate) + ' at ' + str(current_time) + '\r\n'

        if not self.offline:
            log = {'method': 'removeBid', 'market': market.market, 'symbol': market.symbol,
                   'rate': bid_rate, 'timestamp': current_time}
            self.db.db_safe_insert('online_transactions', log)
            #self.pushbullet.push(message, 'Remove crypto')

        with open('./log.txt', 'a', encoding='UTF-8') as log_file:
            log_file.write(message)

    @staticmethod
    def log_error(error):
        with open('./log.txt', 'a', encoding='UTF-8') as log_file:
            log_file.write(
                'Error: ' + error + ' At ' + str(datetime.now()) + '\r\n')