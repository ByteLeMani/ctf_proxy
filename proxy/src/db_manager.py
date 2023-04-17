from src.constants import DB_URL
import threading
import pymongo

lock = threading.Lock()

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
class DBManager(metaclass=Singleton):
    def __init__(self):
        self.client = pymongo.MongoClient(DB_URL)
        self.db = self.client.db

    def close(self):
        self.client.close()