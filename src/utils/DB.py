from datetime import datetime
import time
import pymongo
from pymongo import errors

class DB:
    def __init__(self, config):
        self.client = pymongo.MongoClient(
            'MONGO_PATH')
    
    def get_tickers(self, collection, sort = -1, limit = 0):
        return self.client.bitteamdb[collection].find({}, 
        {'price': 1, 'bid': 1, 'ask': 1, 'date': 1, '_id': False}).sort([('date', sort)]).limit(limit)
    
    def db_safe_insert(self, collection, document):
        for i in range(5):
            try:
                self.client.bitteamdb[collection].insert_one(document)
                break
            except pymongo.errors.AutoReconnect:
                with open('./log.txt', 'a', encoding='UTF-8') as log_file:
                    log_file.write(
                        'Error: ' + str(datetime.utcnow()) + ' AutoReconnect' + ' At ' + str(datetime.now()) + '\r\n')
                time.sleep(pow(2, i))
