from pymongo import MongoClient
from bson import ObjectId, DBRef

# Connection details
mongo_uri = "mongodb://egemenNewcheAdmin:passNewche@localhost:27017/newcheDB"
client = MongoClient(mongo_uri)

# Database and collection handles
db = client['newcheDB']
unprocessedNews = db['unprocessedNews']
backupNews = db['backupNews']
news = db['news']
tags = db['tag']

# Backup the first unprocessedNews item to backupNews
print("Starting backup of the first unprocessed news item...")
for item in unprocessedNews.find():  
    if not backupNews.find_one({'_id': item['_id']}):
        backupNews.insert_one(item)
        print(f"Backup completed for item with ID: {item['_id']}.")

# Process and move the first item from unprocessedNews to news
print("Processing the first news item...")
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
        
        # Insert the processed item into the news collection
        news.insert_one(item)
        print(f"Processed and inserted news item: '{item['title']}' with ID: {item['_id']}")

        # Delete the processed item from unprocessedNews
        unprocessedNews.delete_one({'_id': item['_id']})
        print("-"*100)
        print("-"*100)
        
        # Exit the loop after processing the first item
        

print("Processing completed for news item.")
