import requests

settings = {
        'exchange': 'Bit2C',
        'symbols': ['BTCNIS'],
        'fiatSymbol': 'ILS',
        'apiUrl': 'https://www.bit2c.co.il/Exchanges/BtcNis/Ticker.json',
        'lastPrice': 'll',
        'bid': 'h',
        'ask': 'l',
        'nested': ''
    }

class Bit2c:
    def getTicker(self, coin):
        aaa = settings.symbols
        url = "https://www.bit2c.co.il/Exchanges/" + coin + "/Ticker.json"
        response = requests.request("GET", url)
        return response.text