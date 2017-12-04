import requests
import json
import time

ratioList = []

def main():
 index = 0
 bittrexAvg = 11126.0 * 3.49
 bit2cAvg = 40700.60782700422

 while True:
     # bit2CTicker = getBit2CTicker()
     # bittrexTicker = getBittrexTicker()
     # bit2cAvg = bit2CTicker["av"]
     # bittrexAvg = float(bittrexTicker["mid"])

     bit2cAvg = getBit2CAverage(bit2cAvg)
     bittrexAvg = getBitterexAverage(bittrexAvg)

     ratio = bit2cAvg / bittrexAvg
     if index == 0:
         index = index + 1
         addNewRatio(ratio)
         continue

     currentRatioAverege = getRatioAverege()
     print('bit2cAvg: ' + str(bit2cAvg))
     print('bittrexAvg: ' + str(bittrexAvg))
     print('ratio: ' + str((ratio - currentRatioAverege) / ratio * 100))
     print('\n\n')
     addNewRatio(ratio)
     time.sleep(3)


def addNewRatio(ratio):
    if (len(ratioList) == 2):
        del ratioList[0]
        ratioList.append(ratio)
    else:
        ratioList.append(ratio)

def getRatioAverege():
    return sum(ratioList) / len(ratioList)

def getBit2CTicker():
    req = requests.get("https://www.bit2c.co.il/Exchanges/BtcNis/Ticker.json")
    ticker = json.loads(req.content)
    return ticker

def getBitterexAverage(average):
    average = average + 1
    return average

def getBit2CAverage(average):
    return average

if __name__ == '__main__':
    main()