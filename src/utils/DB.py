from datetime import datetime
import time
import pymongo
from pymongo import errors

class DB:
    def __init__(self, config):
        self.client = pymongo.MongoClient(
            'mongodb://bitteamisrael:Ariel241096@ds135667-a0.mlab.com:35667,ds135667-a1.mlab.com:35667/bitteamdb?replicaSet=rs-ds135667')
    
    def get_tickers(self, collection, limit):
        return self.client.bitteamdb[collection].find({}, 
        {'bid': 1, '_id': False}).sort([('date', pymongo.DESCENDING)]).limit(limit)
    
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
