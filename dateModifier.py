from pymongo import MongoClient
import datetime

# Establish the database connection
client = MongoClient("mongodb://egemenNewcheAdmin:passNewche@localhost:27017/newcheDB")
db = client['newcheDB']
news_collection = db['news']

# Fetch all documents in the collection
all_documents = news_collection.find()

for document in all_documents:
    # Extract the original date-time from the document
    original_date_time = document['date']
    
    # Check if the date is in the unwanted format, for example, checking if it contains a time component
    try:
        # Attempt to parse the date-time string to a datetime object
        date_time = datetime.datetime.fromisoformat(original_date_time.rstrip('Z'))
        
        # If successful, format to date-only string
        modified_date_only = date_time.strftime('%Y-%m-%d')
        
        # Check if the original date-time is already in the 'YYYY-MM-DD' format
        if original_date_time != modified_date_only:
            print("Updating Date for Title:", document.get('title', 'No Title Provided'))
            print("Original Date:", original_date_time)
            print("Modified Date:", modified_date_only)
            print("------------------------------------------------------------------------")
            
            # Update the date field in the database (uncomment the following line to execute)
            news_collection.update_one(
                {'_id': document['_id']},
                {'$set': {'date': modified_date_only}}
            )
        else:
            print("No update needed for Title:", document.get('title', 'No Title Provided'))
            print("Date is already in correct format:", original_date_time)
            print("------------------------------------------------------------------------")
    except ValueError:
        print("Date format error for Title:", document.get('title', 'No Title Provided'))
        print("Invalid Date Format:", original_date_time)
        print("------------------------------------------------------------------------")
        # Optionally handle the error, e.g., by logging or correcting the format
