from pymongo import MongoClient

uri = "mongodb://egemenNewcheAdmin:passNewche@localhost:27017/newcheDB"

# Connect to the MongoDB client
client = MongoClient(uri)
# Select the database
db = client['newcheDB']
# Select the collection
collection = db['unprocessedNews']

