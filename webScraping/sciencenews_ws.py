import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
import feedparser

# URL of the RSS feed
feed_url = "https://www.sciencenews.org/feed"

# Parse the feed
feed = feedparser.parse(feed_url)

print("Extracting article URLs...")
# Extract and print article URLs
article_urls = [entry.link for entry in feed.entries]

for url in article_urls:
    print("URL found: "+ url)
    
def parse_article(url):
    print(f"Fetching full article from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
    
        # List of possible selectors for the title, ordered by priority
        title_selectors = [
            {'tag': 'h1', 'class': 'entry-title entry-title--with-subtitle'},  # Original class
            {'tag': 'h1', 'class': 'entry-title'},  # Class observed in your snippet
            # Add more selectors as needed
        ]

        title_tag = None

        # Try each selector until the title is found
        for selector in title_selectors:
            if selector['class']:
                title_tag = soup.find(selector['tag'], class_=selector['class'])
            else:
                title_tag = soup.find(selector['tag'])
            if title_tag:
                break  # Stop the loop if a title is found

        title = title_tag.text.strip() if title_tag else 'Title Not Found'

        # Extract the publication date with error handling
        date_tag = soup.find('time', class_='entry-date published')
        date = date_tag['datetime'].strip() if date_tag else 'Date Not Found'

        # Extract the article content
        article_content = soup.find('div', class_='entry-content')
        paragraphs = article_content.find_all('p') if article_content else []
        content = '\n'.join(paragraph.text.strip() for paragraph in paragraphs)
        
        print("Title: " + title)
        print("Date: " + date)
        print("Content: " + content[:100] + "...\n")
        
        return {
            'title': title,
            'url': url,
            'date': date,
            'content': content,
        }
        print(f"Article fetched successfully: {title}")
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return {"title": "Error", "url": "Error", "date": "Error", "content": "Error"}

news_array = []
# Itarate over articles
for url in article_urls:
    article_data = parse_article(url)
    news_array.append(article_data)