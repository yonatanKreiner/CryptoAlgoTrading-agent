class Ticker:

    def __init__(self, exchange, symbol, fiatsymbol, lastPrice, bid, ask):
        self.exchange = exchange
        self.symbol = symbol
        self.fiatSymbol = fiatsymbol
        self.lastPrice = lastPrice
        self.bid = bid
        self.ask = ask