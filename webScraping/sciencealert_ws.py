import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time

# URL of ScienceAlert
url = "https://www.sciencealert.com/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def extract_articles(url, ):
    print(f"Fetching articles from {url}...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        latest_news_block = soup.find('div', class_='latest-news-block')
        all_articles = latest_news_block.find_all_next('article')

        article_html_array = [str(article) for article in all_articles]
        print("Articles fetched successfully.")
        return article_html_array

    except requests.RequestException as e:
        print(f"Error fetching articles: {e}")
        return []

def extract_article_urls(article_html_array, max_retries=3):
    print("Extracting article URLs...")
    urls = []
    for article_html in article_html_array:
        retries = 0
        while retries < max_retries:
            soup = BeautifulSoup(article_html, 'html.parser')
            article_tag = soup.find('article')
            if article_tag:
                first_link = article_tag.find('a')
                if first_link and 'href' in first_link.attrs:
                    urls.append(first_link['href'])
                    print(f"URL found: {first_link['href']}")
                    break
            retries += 1
            time.sleep(1)
        if retries == max_retries:
            print(f"Failed to find article after {max_retries} retries.")
    return urls

def fetch_articles(url):
    print(f"Fetching full article from {url}...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.find('title').text.replace(" : ScienceAlert", "") if soup.find('title') else "No title found"
        date_meta = soup.find('meta', {'property': 'article:published_time'})
        date = date_meta['content'] if date_meta else "No date found"
        article_section = soup.find('article')
        article_text = article_section.get_text(separator=' ', strip=True) if article_section else "No content found"

        # Extract the article's image
        img_tag = soup.find('meta', {'property': 'og:image'})
        img_url = img_tag['content'] if img_tag else None
        if img_url.startswith('//'):
            img_url = 'https:' + img_url
        img_data = requests.get(img_url).content if img_url else None

        news = {
            "title": title,
            "url": url,
            "date": date,
            "body": article_text,
            "image_url": img_url,
            "img_data": img_data
        }
        print(f"Article fetched successfully: {title}")
        return news

    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return {
            "title": "Error",
            "url": "Error",
            "date": "Error",
            "body": "Error",
            "image_url": None,
            "img_data": None
        }


# Connection URI of MongoDB
uri = ".../newcheDB"
# Connect to the MongoDB client
client = MongoClient(uri)
# Select the database
db = client['newcheDB']
# Select the collection
collection = db['unprocessedNews']
url_check = db['news']


article_html_array = extract_articles(url)
all_article_urls = extract_article_urls(article_html_array)
print("\n")

article_urls = []

for url in all_article_urls:
    if not url_check.find_one({"url": url}):
        article_urls.append(url)
        print("New url will be added: "+ url)
    else:
        print(f"URL already in database, skipping: {url}")

news_array = []

for url in article_urls:
    news_article = fetch_articles(url)
    news_array.append(news_article)

print("Adding articles to MongoDB...")

for news_article in news_array:
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
print("Disconnected from MongoDB.")
