import pymongo

class DbManager(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DbManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://db:27017/")
        self.ctf_db = self.client.ctf_db

    def close(self):
        self.client.close()

# Usage example - Inside http_service module:
# def giftCard(self ,stream:HTTPStream):
#     message = stream.current_http

#     db = DbManager().ctf_db.http_service
    
#     if "GET" in message.method and "card" in message.parameters:
#         cardNumber = message.parameters.get("card")
#         print(cardNumber)
#         item = {"cardNumber" : cardNumber }
#         if db.find_one(item):
#             return True
#         else:
#             db.insert_one(item)
#             return False