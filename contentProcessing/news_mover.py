from pymongo import MongoClient, errors
from bson import DBRef

# Connection details
mongo_uri = ".../newcheDB"
client = MongoClient(mongo_uri)

# Database and collection handles
db = client['newcheDB']
unprocessedNews = db['unprocessedNews']
backupNews = db['backupNews']
news = db['news']
tags = db['tag']

try:
    # Backup all unprocessedNews items to backupNews
    print("Starting backup of unprocessed news items...")
    for item in unprocessedNews.find():
        if not backupNews.find_one({'_id': item['_id']}):
            backupNews.insert_one(item)
            print(f"Backup completed for item with ID: {item['_id']}.")
        else:
            print(f"Item with ID: {item['_id']} already exists in backup.")

    # Process and move all items from unprocessedNews to news
    print("Processing news items...")
    for item in unprocessedNews.find():
        print(f"News ID: {item['_id']}, URL: {item.get('url', 'URL not provided')}")
        
        if 'tags' in item and item['tags']:
            processed_tags = []

            for i, tag_name in enumerate(item['tags']):
                tag_name_lower = tag_name.lower()
                # Check if the tag exists
                tag_doc = tags.find_one({'name': tag_name_lower})

                if not tag_doc:
                    # Tag doesn't exist, so insert it
                    tag_id = tags.insert_one({
                        'name': tag_name_lower,
                        'displayName': tag_name,
                        '_class': "com.newche.model.Tag",
                        'level': min(i, 4)  # Level calculation
                    }).inserted_id
                    print(f"Inserted new tag: '{tag_name}' with ID: {tag_id}")
                else:
                    tag_id = tag_doc['_id']
                    print(f"Tag already exists: '{tag_name}' with ID: {tag_id}")

                # Add the DBRef to the processed tags
                processed_tags.append(DBRef('tag', tag_id))

            # Update the item with processed tags and class
            item['tags'] = processed_tags
            item['_class'] = "com.newche.model.News"
            
            # Create a copy of the item without the 'body' field for insertion into the news collection
            item_copy = item.copy()
            item_copy.pop('body', None)
            
            # Insert the processed item (without body) into the news collection
            news.insert_one(item_copy)
            print(f"Processed and inserted news item: '{item['title']}' with ID: {item['_id']}")

            # Delete the processed item from unprocessedNews
            unprocessedNews.delete_one({'_id': item['_id']})
            print(f"Deleted processed news item with ID: {item['_id']} from unprocessedNews.")
        else:
            print("No tags found for the item, skipping tag processing.")
        print("-" * 100)

    print("Processing completed for all news items.")
except errors.PyMongoError as e:
    print(f"An error occurred: {e}")
finally:
    client.close()
