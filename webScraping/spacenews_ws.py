import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
import feedparser
from PIL import Image
from bson.binary import Binary
import io
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection URI of MongoDB
uri = "mongodb://egemenNewcheAdmin:passNewche@localhost:27017/newcheDB"
client = MongoClient(uri)
db = client['newcheDB']
collection = db['unprocessedNews']
url_check = db['news']

feed_url = "https://spacenews.com/section/news-archive/feed/"

# Headers for requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def download_and_process_image(image_url):
    try:
        response = requests.get(image_url, headers=headers)
        image = Image.open(io.BytesIO(response.content))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
    except Exception as e:
        logger.error(f"Error processing image from {image_url}: {e}")
        return None

def parse_article(url):
    logger.info(f"Fetching full article from {url}...")
    try:
        response = requests.get(url, headers=headers)
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

        logger.info(f"Title: {title}\nDate: {date}\nContent: {content[:100]}...")

        return {
            'title': title,
            'url': url,
            'date': date,
            'body': content,
            'image_url': image_url,
            'image_data': Binary(image_data) if image_data else None
        }
    except requests.RequestException as e:
        logger.error(f"Error fetching the page {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error processing {url}: {e}")
        return None

# Parse the feed
feed = feedparser.parse(feed_url)

# Extract and process articles
all_article_urls = [entry.link for entry in feed.entries]
article_urls = [url for url in all_article_urls if not url_check.find_one({"url": url})]

news_array = []
for url in article_urls:
    news_article = parse_article(url)
    if news_article:
        news_array.append(news_article)

logger.info("\n" + "-"*100 + "\n")

# Save articles to MongoDB
for news_article in news_array:
    try:
        # Check if the article is a duplicate by both title and URL
        if not collection.find_one({"title": news_article['title'], "url": news_article['url']}):
            collection.insert_one(news_article)
            logger.info(f"Inserted article: {news_article['title']}")
        else:
            logger.info(f"Duplicate article found, skipping: {news_article['title']} - {news_article['url']}")
    except Exception as e:
        logger.error(f"Error inserting article {news_article['title']}: {e}")

client.close()
logger.info("\nDisconnected from MongoDB.")
