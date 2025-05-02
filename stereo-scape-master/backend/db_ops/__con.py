import pymongo

client = pymongo.MongoClient(f'mongodb://localhost:27017')
db = client['stereoscape']

