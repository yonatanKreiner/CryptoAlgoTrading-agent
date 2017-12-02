import requests
import json

def main():
 absuluteRatio = 1.02
 bit2CTicker = getBit2CTicker()
 bittrexTicker = getBittrexTicker()

 while True:
     bit2cAvg = bit2CTicker["av"]
     bittrexAvg = bittrexTicker["mid"]
     changeRatio = bit2cAvg / bittrexAvg
     breakEven = percentBreakEven(bit2CTicker)

     if changePrecent > breakEven {

     }





def percentBreakEven(ticker):
    comssion = 0.5
    space = 0.5
    bid = ticker["h"]
    ask = ticker["l"]
    breakEven = bid / ask

def getBit2CTicker():
    req = requests.get("https://www.bit2c.co.il/Exchanges/BtcNis/Ticker.json")
    ticker = json.loads(req.content)

def getBittrexTicker():
    req = requests.get("https://api.bitfinex.com/v1/pubticker/dshusd")
    ticker = json.loads(req.content)

if __name__ == '__main__':
    main()