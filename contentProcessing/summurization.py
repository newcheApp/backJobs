'''
The Summurization Model Used from Hugging Face
(https://huggingface.co/facebook/bart-large-cnn?text=Artemis+moon+astronauts+will+need+oxygen.+NASA+wants+to+extract+it+from+lunar+dust%0D%0A%0D%0ANASA+wants+to+figure+out+how+future+moon-dwellers+can+produce%2C+capture+and+store+breathable+oxygen+from+lunar+soil.%0D%0A%0D%0AEven+though+the+day+when+humans+live+and+work+on+the+moon+is+still+in+the+unidentified+future%2C+NASA+is+actively+planning+for+how+to+get+us+there.+%0D%0A%0D%0ATo+help+one+day+provide+the+resources+needed+for+a+sustainable+human+presence+on+the+moon%2C+the+agency%27s+Space+Technology+Mission+Directorate+%28STMD%29+is+seeking+input+on+methods+to+extract+of+oxygen+from+moon+dust.+This+request+will%2C+in+theory%2C+allow+industry+and+researchers+to+provide+details+on+technologies+that+enable+future+moon-dwellers+to+produce%2C+capture%2C+and+store+breathable+oxygen+from+lunar+soil.+NASA+hopes+to+use+the+information+it+gathers+to+develop+a+technology+demo.%0D%0A%0D%0AThis+concept+of+using+materials+found+on+other+bodies+to+make+vital+resources%2C+rather+than+shipping+them+from+Earth%2C+is+known+as+in-situ+resource+utilization%2C+or+ISRU.+%22Using+in-situ+resources+is+essential+to+making+a+sustained+presence+farther+from+Earth+possible.+Just+as+we+need+consumables+and+infrastructure+to+live+and+work+on+our+home+planet%2C+we%27ll+need+similar+support+systems+on+the+moon+for+crew+and+robots+to+operate+safely+and+productively%2C%22+Prasun+Desai%2C+NASA%27s+acting+associate+administrator+of+STMD%2C+said+in+a+statement+announcing+the+Request+for+Information%2C+or+RFI.%0D%0A%0D%0AAs+support+for+this+concept%2C+NASA+pointed+to+the+Perseverance+Mars+rover%27s+MOXIE+experiment%2C+which+repeatedly+transformed+carbon+dioxide+from+the+Martian+atmosphere+into+breathable+oxygen.+Though+MOXIE+only+produced+about+0.2+ounces+%286+grams%29+%E2%80%94+about+equivalent+to+a+small+tree+on+Earth+%E2%80%94+its+preliminary+tests+nevertheless+proved+the+first+time+that+a+human+device+created+oxygen+on+another+world.%0D%0A%0D%0ANASA+believes+a+similar+technology+would+be+a+tremendous+boon+to+astronauts+who+will+spend+time+on+the+moon+in+the+future+as+part+of+its+Artemis+program.+Producing+oxygen+on+the+moon+means+that+astronauts+need+to+carry+less+of+it+with+them%2C+saving+valuable+weight+and+allowing+them+to+stay+off-Earth+for+longer+missions.+%0D%0A%0D%0ABefore+actually+having+astronauts+try+making+oxygen+for+themselves%2C+however%2C+NASA+plans+to+showcase+the+tech+to+do+so+as+part+of+a+demonstration+it+calls+the+Lunar+Infrastructure+Foundational+Technologies+%28LIFT-1%29.+%0D%0A%0D%0AIn-situ+resource+utilization%2C+turning+readily+available+materials+on+other+worlds+into+resources+like+oxygen%2C+water%2C+and+metal%2C+is+one+of+the+research+areas+NASA+supports+via+its+Lunar+Surface+Innovation+Initiative.+NASA+conducts+its+own+research+and+partners+with+external+researchers+to+study+living+on+the+moon%2C+looking+into+how+to+build+lunar+infrastructure%2C+how+to+power+that+infrastructure%2C+and+how+to+protect+that+infrastructure+from+the+lunar+elements.+LIFT-1+may+include+demonstrations+of+these+technologies%2C+too.):

@article{DBLP:journals/corr/abs-1910-13461,
  author    = {Mike Lewis and
               Yinhan Liu and
               Naman Goyal and
               Marjan Ghazvininejad and
               Abdelrahman Mohamed and
               Omer Levy and
               Veselin Stoyanov and
               Luke Zettlemoyer},
  title     = {{BART:} Denoising Sequence-to-Sequence Pre-training for Natural Language
               Generation, Translation, and Comprehension},
  journal   = {CoRR},
  volume    = {abs/1910.13461},
  year      = {2019},
  url       = {http://arxiv.org/abs/1910.13461},
  eprinttype = {arXiv},
  eprint    = {1910.13461},
  timestamp = {Thu, 31 Oct 2019 14:02:26 +0100},
  biburl    = {https://dblp.org/rec/journals/corr/abs-1910-13461.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
'''

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
