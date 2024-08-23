from pymongo import MongoClient
import datetime

# Establish the database connection
client = MongoClient("../newcheDB")
db = client['newcheDB']
news_collection = db['unprocessedNews']

# Fetch all documents in the collection
all_documents = news_collection.find()

# Iterate over each document
for document in all_documents:
    # Extract the original date field from the document
    original_date = document['date']
    
    # Check if the date field is a string
    if isinstance(original_date, str):
        try:
            # Attempt to parse the date string to a datetime object assuming ISO 8601 format
            new_date = datetime.datetime.fromisoformat(original_date.rstrip('Z'))
            
            # Update the date field in the database with the new datetime object
            news_collection.update_one(
                {'_id': document['_id']},
                {'$set': {'date': new_date}}
            )
            print(f"Updated document {document['_id']} with new datetime type.")
        
        except ValueError as e:
            # Log or handle parsing errors if the date format does not match
            print(f"Failed to parse date for document {document['_id']}: {e}")
    else:
        # Skip updating if the date is not a string
        print(f"No update needed for document {document['_id']}; date is not a string.")


# Close the MongoDB connection
client.close()


