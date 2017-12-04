import requests
import json
import time

ratioList = []

def main():
 averageInterval = 0
 index = 0
 allaverage = 0
 changeRatioAll = 0

 while True:
     bit2CTicker = getBit2CTicker()
     bittrexTicker = getBittrexTicker()
     bit2cAvg = bit2CTicker["av"]
     bittrexAvg = float(bittrexTicker["mid"])

     ratio = bit2cAvg / bittrexAvg
     if index == 0:
         index = index + 1
         addNewRatio(ratio)
         continue

     currentRatioAverege = getRatioAverege()
     if ((currentRatioAverege - ratio) * 100 > 0.1) :
         print((currentRatioAverege - ratio) * 100)

     addNewRatio(ratio)
     time.sleep(3)


def addNewRatio(ratio):
    if (len(ratioList) == 30):
        del ratioList[0]
        ratioList.append(ratio)
    else:
        ratioList.append(ratio)

def getRatioAverege():
    return sum(ratioList) / len(ratioList)

def percentBreakEven(ticker):
    comssion = 0.5
    space = 0.5
    bid = ticker["h"]
    ask = ticker["l"]
    breakEven = bid / ask

def getBit2CTicker():
    req = requests.get("https://www.bit2c.co.il/Exchanges/BtcNis/Ticker.json")
    ticker = json.loads(req.content)
    return ticker

def getBittrexTicker():
    req = requests.get("https://api.bitfinex.com/v1/pubticker/btcusd")
    ticker = json.loads(req.content)
    return ticker

if __name__ == '__main__':
    main()