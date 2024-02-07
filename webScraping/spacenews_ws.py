import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
import feedparser
from PIL import Image
from bson.binary import Binary
import io

# Connection URI of MongoDB
uri = "mongodb://egemenNewcheAdmin:passNewche@localhost:27017/newcheDB"
client = MongoClient(uri)
db = client['newcheDB']
collection = db['unprocessedNews']

feed_url = "https://spacenews.com/section/news-archive/feed/"

def download_and_process_image(image_url):
    try:
        response = requests.get(image_url)
        image = Image.open(io.BytesIO(response.content))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def parse_article(url):
    print(f"\nFetching full article from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        title, date, content = 'Title Not Found', 'Date Not Found', 'Content Not Found'

        title_tag = soup.find('h1', class_='entry-title')
        if title_tag:
            title = title_tag.text.strip()

        date_tag = soup.find('time', class_='entry-date published')
        if date_tag:
            date = date_tag['datetime'].strip()

        article_content = soup.find('div', class_='entry-content')
        if article_content:
            paragraphs = article_content.find_all('p')
            content = '\n'.join(paragraph.text.strip() for paragraph in paragraphs)

        # Attempt to find the main image URL
        image_tag = soup.find('meta', property='og:image')
        image_url = image_tag['content'] if image_tag else None

        # Optionally download and process the image
        image_data = None
        if image_url:
            image_data = download_and_process_image(image_url)

        print(f"Title: {title}\nDate: {date}\nContent: {content[:100]}...")

        return {
            'title': title,
            'url': url,
            'date': date,
            'body': content,
            'image_url': image_url,
            'image_data': Binary(image_data) if image_data else None
        }
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None

# Parse the feed
feed = feedparser.parse(feed_url)

# Extract and process articles
all_article_urls = [entry.link for entry in feed.entries]
article_urls = [url for url in all_article_urls if not collection.find_one({"url": url})]

news_array = [parse_article(url) for url in article_urls]

# Save articles to MongoDB
for news_article in news_array:
    if news_article and not collection.find_one({"title": news_article['title']}):
        collection.insert_one(news_article)
        print(f"Inserted article: {news_article['title']}")
    else:
        print(f"Duplicate article found or error occurred, skipping: {news_article.get('title', 'Unknown')}")

client.close()
print("\nDisconnected from MongoDB.")
