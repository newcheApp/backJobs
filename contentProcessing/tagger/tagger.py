from pymongo import MongoClient
import openai
import json
from bson import ObjectId
from openai import OpenAI
client = OpenAI()

# Connection URI
uri = "mongodb://egemenNewcheAdmin:passNewche@localhost:27017/newcheDB"
# Connect to the MongoDB client
client = MongoClient(uri)
# Select the database
db = client['newcheDB']
# Select the collection
collection = db['unprocessedNews']

def gather_news_id_and_summary():
    # Query to find documents where tags array is empty or tags field does not exist
    query = {
        "$or": [
            {"tags": {"$exists": False}},  # Tags field does not exist
            {"tags": {"$size": 0}}         # Tags array is empty
        ]
    }
    # Projection to specify only to return the _id and summary fields
    projection = {
        "_id": 1,
        "summary": 1
    }
    # Find documents based on the query and projection
    news_items = collection.find(query, projection)
    
    # Convert the cursor to a list (optional, depending on your use case)
    news_list = list(news_items)
    
    print(f"Retrieved {len(news_list)} news items without tags.")
    return news_list

# Call the function and store the result
news_without_tags = gather_news_id_and_summary()

# Depending on your application, you can print, return, or process the news_list further.
# For example, to print each news item:
print("News gathered... \n")
print(news_without_tags[0])
    
def save_first_3_news_as_string(news_list):
    # Initialize an empty string to store the formatted news
    news_string = ""
    # Loop through the first 3 news items in the list
    for news in news_list[:2]:
        # Format each news item and append it to the news_string
        news_string += f"ID: {news['_id']} \nSUMMARY: {news.get('summary')}\n\n"
    return news_string


news_string_result = save_first_3_news_as_string(news_without_tags)



from openai import OpenAI
client = OpenAI()

def generate_tags_for_news_batch_json(news_string_result):
    prompt_base = """Generate multi-level clustering tags for the following news summaries in JSON format. Each level should allow for multiple tags, progressively narrowing down the focus from the broadest category to the most specific details. Format the output as a JSON object with "id" as the news ID and "tags" as a dictionary containing arrays of tags for each level.

Tagging structure should be as follows:
- Level 1: The broadest category covering the general subject of the news, such as broad sectors including but not limited to sports, health, technology.
- Level 2: Sub-categories within the broad sector, focusing on more specific domains or types within the general subject.
- Level 3: Even more specific themes, types, or areas within the sub-category, detailing particular aspects or fields.
- Level 4: Detailed elements, focusing on very specific outcomes, implications, or aspects within the themes or areas identified in Level 3.
- Level 5: The most detailed tags, pinpointing precise topics, events, technologies, or outcomes mentioned in the news summary.

Analyze each news summary to identify appropriate tags for each level, ensuring that the tags are relevant and specific to the content of the news. Avoid using the provided examples; instead, derive tags directly from the summary.

Please provide tags for each level without using the provided examples, ensuring that the tags reflect the content of the news summary accurately. and do not write result in "```json\n```", do not specify the format you give me just give the result in response. and always give in the json format of: {
    "id": "65bd4560d17b3317bdff94ae",
    "tags": {
        "Level 1": ["Sports"],
        "Level 2": ["Motorsport"],
        "Level 3": ["Formula 1"],
        "Level 4": ["Entry Rejection"],
        "Level 5": ["Andretti Cadillac Team"]
    }
}
"""

    prompt = prompt_base + news_string_result + "\n\nProvide the tags for each news item formatted as specified."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Please generate the tags for each news item formatted as specified above."}
        ]
    )

    # Assuming the last message in the response is what we're interested in
    if response.choices and response.choices[0].message:
        gpt_result = response.choices[0].message.content
    else:
        gpt_result = "No response generated."

    print("Tags generation requested.")
    return gpt_result



# Call the function and store the output in `gpt_result`
gpt_result = generate_tags_for_news_batch_json(news_string_result)

# Assuming you want to print or further process the `gpt_result`
print(gpt_result)

json_strings = gpt_result.strip().split('\n\n')

tags_data = [json.loads(json_str) for json_str in json_strings]


def preprocess_tags_data(tags_data):
    print("Original tags data:")
    for item in tags_data:
        print(item)
    
    standardized_tags_data = []

    for item in tags_data:
        # If the item already has the 'id' key, it's in the desired format.
        if 'id' in item:
            standardized_tags_data.append(item)
        else:
            # The item is in the alternate format where the key is the ID.
            tag_id, tag_info = next(iter(item.items()))
            standardized_item = {
                "id": tag_id,
                "tags": tag_info['tags']
            }
            standardized_tags_data.append(standardized_item)
    
    print("\nStandardized tags data:")
    for item in standardized_tags_data:
        print(item)
    
    return standardized_tags_data


def convert_to_objectid(doc_id):
    try:
        # Validate if doc_id is already an ObjectId
        if isinstance(doc_id, ObjectId):
            return doc_id
        
        # Check if doc_id is in ObjectId format
        if len(doc_id) == 24 and all(c in "0123456789abcdef" for c in doc_id):
            mongo_id = ObjectId(doc_id)
            return mongo_id
        else:
            raise ValueError("Invalid ObjectId format")
    except Exception as e:
        # If conversion fails, handle the exception (e.g., print an error message)
        print(f"Error converting '{doc_id}' to ObjectId: {e}")
        return None  # Return None or any other value to indicate failure

def process_tags_data(tags_data, news_list):
    processed_count = 0
    updated_count = 0
    not_found_count = 0

    for tag_item in tags_data:
        tag_id = tag_item['id']
        corresponding_news_item = next((item for item in news_list if str(item['_id']) == tag_id), None)
        
        if not corresponding_news_item:
            print(f"ID not found: {tag_id}")
            not_found_count += 1
            continue
        
        doc_summary = corresponding_news_item['summary']
        tags_array = [tag for level_tags in tag_item['tags'].values() for tag in level_tags]
        
        result = collection.update_one({"summary": doc_summary}, {"$set": {"tags": tags_array}})
        
        if result.matched_count == 0:
            not_found_count += 1
        else:
            updated_count += 1
        
        processed_count += 1
        
        # Optional: You can add a print statement here to indicate progress, e.g., every 100 items
        if processed_count % 100 == 0:
            print(f"Processed {processed_count} items...")
    
    print(f"Processing complete. Total processed: {processed_count}, Updated: {updated_count}, Not found: {not_found_count}.")

# Preprocess the tags_data to standardize its format
standardized_tags_data = preprocess_tags_data(tags_data)

# Then, use the standardized_tags_data in your existing process_tags_data function
process_tags_data(standardized_tags_data, news_without_tags)

# Count the number of items in the list
news_count = len(news_without_tags)

# Print the count
print("Number of news summaries without tags:", news_count)