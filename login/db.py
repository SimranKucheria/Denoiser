import pymongo

client = pymongo.MongoClient('localhost', 27017)
db = client.can_you_hear_me
