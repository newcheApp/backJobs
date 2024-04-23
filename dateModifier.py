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
    original_date_time = document.get('date', '')

    # Attempt to convert the original ISO date-time string to a datetime object and then to just a date string
    try:
        # Handle cases where the 'Z' timezone suffix is present
        if original_date_time.endswith('Z'):
            original_date_time = original_date_time.rstrip('Z')
        date_time = datetime.datetime.fromisoformat(original_date_time)
        modified_date_only = date_time.strftime('%Y-%m-%d')
    except ValueError:
        # Handle cases where the date is not a valid ISO format string
        modified_date_only = 'Invalid date format'

    # Print title, old date-time, and modified date-only
    print("Title:", document.get('title', 'No Title Provided'))
    print("Original Date:", document.get('date', 'No Date Provided'))
    print("Modified Date:", modified_date_only)
    print("------------------------------------------------------------------------")
