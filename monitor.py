import requests
import json
import time
from requests.exceptions import ConnectionError
import os
from os import environ
from flask import Flask

def main():

    os.makedirs("Data", exist_ok=True)
    exchangeToSymbols = [
        {
            'exchange': 'Bit2C',
            'symbols': 'BTCNIS',
            'fiatSymbol': 'ILS',
            'apiUrl': 'https://www.bit2c.co.il/Exchanges/BtcNis/Ticker.json',
            'lastPrice': 'll',
            'bid': 'h',
            'ask': 'l',
            'nested': ''
        }, {
            'exchange': 'Bit2C',
            'symbols': 'LTCNIS',
            'fiatSymbol': 'ILS',
            'apiUrl': 'https://www.bit2c.co.il/Exchanges/LtcNis/Ticker.json',
            'lastPrice': 'll',
            'bid': 'h',
            'ask': 'l',
            'nested': ''
        }, {
            'exchange': 'Bit2C',
            'symbols': 'BCHNIS',
            'fiatSymbol': 'ILS',
            'apiUrl': 'https://www.bit2c.co.il/Exchanges/BchNis/Ticker.json',
            'lastPrice': 'll',
            'bid': 'h',
            'ask': 'l',
            'nested': ''
        }, {
            'exchange': 'Bitfinex',
            'symbols': 'BTCUSD',
            'fiatSymbol': 'USD',
            'apiUrl': 'https://api.bitfinex.com/v1/pubticker/btcusd',
            'lastPrice': 'last_price',
            'bid': 'bid',
            'ask': 'ask',
            'nested': ''
        }, {
            'exchange': 'Bitfinex',
            'symbols': 'LTCUSD',
            'fiatSymbol': 'USD',
            'apiUrl': 'https://api.bitfinex.com/v1/pubticker/ltcusd',
            'lastPrice': 'last_price',
            'bid': 'bid',
            'ask': 'ask',
            'nested': ''
        }, {
            'exchange': 'Bitfinex',
            'symbols': 'ETHUSD',
            'fiatSymbol': 'USD',
            'apiUrl': 'https://api.bitfinex.com/v1/pubticker/ethusd',
            'lastPrice': 'last_price',
            'bid': 'bid',
            'ask': 'ask',
            'nested': ''
        }, {
            'exchange': 'Bitfinex',
            'symbols': 'BCHUSD',
            'fiatSymbol': 'USD',
            'apiUrl': 'https://api.bitfinex.com/v1/pubticker/bchusd',
            'lastPrice': 'last_price',
            'bid': 'bid',
            'ask': 'ask',
            'nested': ''
        }, {
            'exchange': 'Bitfinex',
            'symbols': 'DASHUSD',
            'fiatSymbol': 'USD',
            'apiUrl': 'https://api.bitfinex.com/v1/pubticker/dshusd',
            'lastPrice': 'last_price',
            'bid': 'bid',
            'ask': 'ask',
            'nested': ''
        }, {
            'exchange': 'Nevbit',
            'symbols': 'BTCPLN',
            'fiatSymbol': 'PLN',
            'apiUrl': 'https://nevbit.com/data/btcpln/ticker.json',
            'lastPrice': 'last',
            'bid': 'buy',
            'ask': 'sell',
            'nested': ''
        }, {
            'exchange': 'Nevbit',
            'symbols': 'LTCPLN',
            'fiatSymbol': 'PLN',
            'apiUrl': 'https://nevbit.com/data/ltcpln/ticker.json',
            'lastPrice': 'last',
            'bid': 'buy',
            'ask': 'sell',
            'nested': ''
        }, {
            'exchange': 'Bitcointrade',
            'symbols': 'BTCBRL',
            'fiatSymbol': 'BRL',
            'apiUrl': 'https://api.bitcointrade.com.br/v1/public/BTC/ticker',
            'lastPrice': 'last',
            'bid': 'buy',
            'ask': 'sell',
            'nested': 'data'
        }, {
            'exchange': 'TheRockTrading',
            'symbols': 'ETHEUR',
            'fiatSymbol': 'EUR',
            'apiUrl': 'https://api.therocktrading.com/v1/funds/ETHEUR/ticker',
            'lastPrice': 'last',
            'bid': 'bid',
            'ask': 'ask',
            'nested': ''
        }, {
            'exchange': 'DSX',
            'symbols': 'ETHUSD',
            'fiatSymbol': 'USD',
            'apiUrl': 'https://dsx.uk/mapi/ticker/ethusd',
            'lastPrice': 'last',
            'bid': 'buy',
            'ask': 'sell',
            'nested': 'ethusd'
        }, {
            'exchange': 'DSX',
            'symbols': 'BCHUSD',
            'fiatSymbol': 'USD',
            'apiUrl': 'https://dsx.uk/mapi/ticker/bccusd',
            'lastPrice': 'last',
            'bid': 'buy',
            'ask': 'sell',
            'nested': 'bccusd'
        }, {
            'exchange': 'Coinroom',
            'symbols': 'DASHPLN',
            'fiatSymbol': 'PLN',
            'apiUrl': 'https://coinroom.com/api/ticker/DASH/PLN',
            'lastPrice': 'last',
            'bid': 'bid',
            'ask': 'ask',
            'nested': ''
        }
    ]
    
    for item in exchangeToSymbols:
        fileHandler = open('Data/%s_%s.csv' % (item['exchange'], item['symbols']), 'a')
        fileHandler.write('Time,Last price,Highest bid,Lowest ask,USD rate\n')
    
    while True:
        for item in exchangeToSymbols:
            try:
                req = requests.get('https://api.fixer.io/latest?base=USD&symbols=%s' % item['fiatSymbol'])
                reqData = json.loads(req.content)
                fiatUsdRate = float(reqData['rates'][item['fiatSymbol']])
            except ValueError:
                fiatUsdRate = 0.0
            except KeyError:
                fiatUsdRate = 0.0
            except ConnectionError:
                fiatUsdRate = 0.0
        
            try:
                req = requests.get(item['apiUrl'])
                reqData = json.loads(req.content)
            except ValueError:
                if item['nested'] != '':
                    reqData[item['nested']] = {}
                    reqData[item['nested']][item['lastPrice']] = 0.0
                    reqData[item['nested']][item['bid']] = 0.0
                    reqData[item['nested']][item['ask']] = 0.0
                else:
                    reqData[item['lastPrice']] = 0.0
                    reqData[item['bid']] = 0.0
                    reqData[item['ask']] = 0.0
            except ConnectionError:
                if item['nested'] != '':
                    reqData[item['nested']] = {}
                    reqData[item['nested']][item['lastPrice']] = 0.0
                    reqData[item['nested']][item['bid']] = 0.0
                    reqData[item['nested']][item['ask']] = 0.0
                else:
                    reqData[item['lastPrice']] = 0.0
                    reqData[item['bid']] = 0.0
                    reqData[item['ask']] = 0.0
        
            fileHandler = open('Data/%s_%s.csv' % (item['exchange'], item['symbols']), 'a')
            if item['nested'] != '':
                fileHandler.write('%s,%f,%f,%f,%f\n' % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), float(reqData[item['nested']][item['lastPrice']]), float(reqData[item['nested']][item['bid']]), float(reqData[item['nested']][item['ask']]), fiatUsdRate))
            else:
                fileHandler.write('%s,%f,%f,%f,%f\n' % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), float(reqData[item['lastPrice']]), float(reqData[item['bid']]), float(reqData[item['ask']]), fiatUsdRate))
        
        time.sleep(1)
    
if __name__ == '__main__':
    app = Flask(__name__)
    app.run(environ.get('PORT'))
    main()