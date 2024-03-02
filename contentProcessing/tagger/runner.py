import subprocess
from pymongo import MongoClient

# MongoDB connection details
mongo_uri = "mongodb://egemenNewcheAdmin:passNewche@localhost:27017/newcheDB"
db_name = "newcheDB"
collection_name = "unprocessedNews"

# Path to your Python interpreter
python_interpreter = "python"

# Relative path to the script you want to run
script_relative_path = "contentProcessing/tagger/tagger.py"

# Create a MongoDB client and select the database and collection
client = MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]

def check_for_untagged_news():
    """
    Checks if there are any news items without tags.
    Returns True if untagged news items exist, False otherwise.
    """
    query = {"$or": [{"tags": {"$exists": False}}, {"tags": {"$size": 0}}]}
    return collection.count_documents(query) > 0

while check_for_untagged_news():
    subprocess.run([python_interpreter, script_relative_path])
    print("Completed one execution cycle. Checking for more untagged news...")

print("No more untagged news items found. Exiting.")
