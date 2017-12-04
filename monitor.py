import requests
import json
import time
from requests.exceptions import ConnectionError
import os


def main():
    os.makedirs("Data", exist_ok=True)
    exchange_to_symbols = json.load(open('./markets.json'))
    
    for item in exchange_to_symbols:
        file_handler = open('Data/%s_%s.csv' % (item['exchange'], item['symbols']), 'a')
        file_handler.write('Time,Last price,Highest bid,Lowest ask,USD rate\n')
    
    while True:
        for item in exchange_to_symbols:
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
        
            file_handler = open('Data/%s_%s.csv' % (item['exchange'], item['symbols']), 'a')
            if item['nested'] != '':
                file_handler.write('%s,%f,%f,%f,%f\n' % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), float(reqData[item['nested']][item['lastPrice']]), float(reqData[item['nested']][item['bid']]), float(reqData[item['nested']][item['ask']]), fiatUsdRate))
            else:
                file_handler.write('%s,%f,%f,%f,%f\n' % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), float(reqData[item['lastPrice']]), float(reqData[item['bid']]), float(reqData[item['ask']]), fiatUsdRate))
        
        time.sleep(1)


if __name__ == '__main__':
    main()