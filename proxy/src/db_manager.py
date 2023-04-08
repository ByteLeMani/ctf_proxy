import pymongo

class DbManager(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DbManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://db:27017/")
        self.db = self.client.db

    def close(self):
        self.client.close()