import pymongo
from src.constants import DB_URL

class DBManager(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.client = pymongo.MongoClient(DB_URL)
        self.db = self.client.db

    def close(self):
        self.client.close()