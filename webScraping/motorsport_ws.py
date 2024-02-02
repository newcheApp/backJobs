import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient

rss_url = 'https://www.motorsport.com/rss/all/news/'
# Connection URI of MongoDB
uri = "mongodb://egemenNewcheAdmin:passNewche@localhost:27017/newcheDB"

def fetch_rss_feed(rss_url):
    # Parse the RSS feed
    feed = feedparser.parse(rss_url)
    news_articles = []

    for entry in feed.entries:
        print(f"Article Found: {entry.title}")
        published_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d %H:%M:%S')
        news_articles.append({
            'title': entry.title,
            'url': entry.link,
            'date': published_date,
            'body': ''  # Placeholder for the body content
        })
        
    return news_articles

def add_article_bodies(news_articles):
    headers = {'User-Agent': 'Mozilla/5.0'}

    for article in news_articles:
        try:
            response = requests.get(article['url'], headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the main content of the article
            article_body = soup.select_one('.ms-article__body, .ms-article__main')
            text_content = ' '.join(p.get_text(strip=True) for p in article_body.find_all('p') if p.get_text(strip=True))
            
            # Find the <h2> tag content and prepend it to the body text
            h2_content = soup.select_one('.text-article-description.font.text-grey-800.mb-6').get_text(strip=True) if soup.select_one('.text-article-description.font.text-grey-800.mb-6') else ''
            full_content = f"{h2_content} {text_content}"
            
            article['body'] = ' '.join(full_content.split())

            print(f"Title: {article['title']}")
            print(f"Date: {article['date']}")
            print(f"url: {article['url']}")
            print(f"Content: {article['body'][:100]}...\n")

            
        except Exception as e:
            print(f"Failed to fetch or parse article at {article['url']}: {e}")
            article['body'] = "Could not fetch the content"


# Connect to the MongoDB client
client = MongoClient(uri)
# Select the database
db = client['newcheDB']
# Select the collection
collection = db['unprocessedNews']

articles = fetch_rss_feed(rss_url)

print("\n")
news_articles = []

for article in articles:
    # Check using 'url' as the key for consistency with database storage
    if not collection.find_one({'url': article['url']}):
        news_articles.append(article)
        print("New article found: "+ article['title'])
    else:
        print(f"Article already in database, skipping: {article['title']}")


add_article_bodies(news_articles)


    
print("\nAdding articles to MongoDB...\n")

for news_article in news_articles:
    # Check if the article already exists in the collection
    existing_article = collection.find_one({"title": news_article['title']})
    if not existing_article:
        # If the article does not exist, insert it into the collection
        collection.insert_one(news_article)
        print(f"Inserted article: {news_article['title']}")
    else:
        # If the article already exists, skip the insertion
        print(f"Duplicate article found, skipping insertion: {news_article['title']}")

client.close()
print("\nDisconnected from MongoDB.")