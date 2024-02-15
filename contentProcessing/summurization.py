from pymongo import MongoClient
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re

# Load the BART model and tokenizer
print(">>> Loading the BART model and tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")

# MongoDB setup
print(">>> Connecting to MongoDB...")
uri = "mongodb://egemenNewcheAdmin:passNewche@localhost:27017/newcheDB"
client = MongoClient(uri)
db = client['newcheDB']
collection = db['unprocessedNews']

def remove_punctuation(text):
    return re.sub(r'[^\w\s\.,\?!]', '', text)

# Function to attempt summarization with retries
def attempt_summarization(text):
    try:
        # First attempt
        return generate_summary(text)
    except Exception as e:
        print(f">>>>>> Initial summarization failed: {e}. Attempting cleanup...")
        try:
            # Attempt after removing punctuation and truncating
            cleaned_text = remove_punctuation(text)
            return generate_summary(cleaned_text[:5000])
        except Exception as e:
            print(f">>>>>> Failed summarization after cleanup: {e}")
            return None

# Function to generate summary
def generate_summary(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs['input_ids'], max_length=130, min_length=30, do_sample=False)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# Count documents that need summaries
docs_to_summarize_count = collection.count_documents({'$or': [{'summary': {'$exists': False}}, {'summary': ''}]})
print(f">>> {docs_to_summarize_count} documents to add...\n")
# Iterate over each document in the collection
for document in collection.find({'$or': [{'summary': {'$exists': False}}, {'summary': ''}]}):  # Filter to only those needing summaries
    try:
        if 'body' in document:
            summary = attempt_summarization(document['body'])
            if summary:
                collection.update_one({'_id': document['_id']}, {'$set': {'summary': summary}})
                print(f">>> {docs_to_summarize_count} - Updated document {document['_id']} with summary...")
            else:
                print(f">>> {docs_to_summarize_count} - Could not generate summary for document {document['_id']}...")
        docs_to_summarize_count -= 1  # Decrement count
    except Exception as e:
        print(f">>>>>> Error processing document {document['_id']}: {e}")

client.close()
