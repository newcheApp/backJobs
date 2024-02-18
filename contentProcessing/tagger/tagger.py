import os
from openai import OpenAI
import json
from pymongo import MongoClient

# Connection URI of MongoDB
uri = "mongodb://egemenNewcheAdmin:passNewche@localhost:27017/newcheDB"
# Connect to the MongoDB client
client = MongoClient(uri)
# Select the database
db = client['newcheDB']
# Select the collection
collection = db['unprocessedNews']

# Query to find news items where the tags are empty or the field does not exist
query = {
    "$or": [
        {"tags": {"$exists": False}},  # Tags field does not exist
        {"tags": {"$size": 0}}  # Tags array is empty
    ]
}

# Projection to include only the _id and summary fields
projection = {
    "_id": 1,
    "summary": 1
}

# Fetch the news items based on the query and projection
unprocessed_news = collection.find(query, projection)

# Store the fetched items in a list for further processing
news_items = list(unprocessed_news)

# Example action: Print the news item IDs and summaries
for news in news_items:
    print(f"ID: {news['_id']}, Summary: {news['summary']}")

# Close the MongoDB connection
client.close()

client = OpenAI()

def generate_tags_for_news_batch_string(news_batch):
    prompt_base = """Generate multi-level clustering tags for the following news summaries. Each level should allow for multiple tags, progressively narrowing down the focus from the broadest category to the most specific details.
    Tagging structure should be as follows:
- Level 1: The broadest category covering the general subject of the news.
- Level 2: Sub-categories within the broad sector.
- Level 3: More specific themes or areas.
- Level 4: Detailed elements focusing on specific outcomes or aspects.
- Level 5: The most detailed tags pinpointing precise topics or events.
Please provide tags for each level without using the provided examples, but rather by analyzing the content of the summary to identify appropriate tags."""

    prompt_news_list = ""
    for news_item in news_batch:
        # Adjusting the key to '_id' if that's what your documents use
        prompt_news_list += f"\n\nID: {news_item['_id']}\nSummary: {news_item['summary']}"

    prompt = prompt_base + prompt_news_list + "\n\nProvide the tags for each news item formatted as specified."

    # Call the OpenAI API with the combined prompt
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant who generates multi-level clustering tags for multiple news summaries."},
            {"role": "user", "content": prompt}
        ]
    )

    # Access the generated text directly
    generated_text = response.choices[-1].message["content"]  # Assuming the correct path to the response content
    return generated_text

# Helper function to chunk the news items list into batches of 10
def chunk_list(data, size=10):
    for i in range(0, len(data), size):
        yield data[i:i + size]

# Initialize a variable to accumulate the generated text
accumulated_text = ""

# Process news items in batches
for batch in chunk_list(news_items):
    generated_text = generate_tags_for_news_batch_string(batch)
    accumulated_text += generated_text + "\n\n"

# Print the accumulated text after processing all batches
print(accumulated_text)
