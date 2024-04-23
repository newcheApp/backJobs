from pymongo import MongoClient
import datetime

# Establish the database connection
client = MongoClient("mongodb://egemenNewcheAdmin:passNewche@localhost:27017/newcheDB")
db = client['newcheDB']
news_collection = db['news']

# Fetch all documents in the collection
all_documents = news_collection.find()

# Print specified fields for each document and modify the date field
for document in all_documents:
    # Extract the original date-time from the document
    original_date_time = document['date']
    
    # Convert the original ISO date-time string to a datetime object and then to just a date string
    date_time = datetime.datetime.fromisoformat(original_date_time.rstrip('Z'))  # Remove 'Z' if it exists
    modified_date_only = date_time.strftime('%Y-%m-%d')
    
    # Print title, old date-time, and modified date-only
    print("Title:", document.get('title', 'No Title Provided'))
    print("Original Date:", original_date_time)
    print("Modified Date:", modified_date_only)
    print("------------------------------------------------------------------------")

# Update the date field in the database (optional, remove comment to execute)
    news_collection.update_one(
        {'_id': document['_id']},
        {'$set': {'date': modified_date_only}}
    )
