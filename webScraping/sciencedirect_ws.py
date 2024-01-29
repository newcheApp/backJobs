import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# Connection URI of MongoDB
uri = "mongodb://egemenNewcheAdmin:passNewche@localhost:27017/newcheDB"
# Connect to the MongoDB client
client = MongoClient(uri)

# Select the database
db = client['newcheDB']

# Select the collection
collection = db['unprocessedNews']

# URL of ScienceAlert
url = "https://www.sciencealert.com/"

# ----------------------------------------- Functions ------------------------------------------

def extract_articles(url):
    try:
        # Send a request to the website
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the 'latest-news-block' div
        latest_news_block = soup.find('div', class_='latest-news-block')

        # Extract all article tags following the latest-news-block div
        all_articles = latest_news_block.find_all_next('article')

        # Store and return the raw HTML of each article
        article_html_array = [str(article) for article in all_articles]
        return article_html_array

    except requests.RequestException as e:
        return f"Error: {e}"

def extract_article_urls(article_html_array):
    urls = []
    for article_html in article_html_array:
        soup = BeautifulSoup(article_html, 'html.parser')
        # Find the first <a> tag within each article
        first_link = soup.article.find('a')
        if first_link and 'href' in first_link.attrs:
            urls.append(first_link['href'])
    return urls

def fetch_articles(url):
    try:
        # Fetch the HTML content from the URL
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text

        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract the title
        title = soup.find('title').text if soup.find('title') else "No title found"
        title = title.replace(" : ScienceAlert", "")
        
        # Extract the date
        date_meta = soup.find('meta', {'property': 'article:published_time'})
        date = date_meta['content'] if date_meta else "No date found"

        # Extract the entire article section
        article_section = soup.find('article')  # Adjust this selector as per the actual structure

        # Extract all text from the article section
        article_text = article_section.get_text(separator=' ', strip=True) if article_section else "No content found"

        # Create a structured news object (dictionary)
        news = {
            "title": title,
            "date": date,
            "content": article_text
        }

        return news

    except requests.RequestException as e:
        return f"Error fetching the page: {e}"

# -------------------------------------- End of Functions --------------------------------------

# Extract articles
article_html_array = extract_articles(url)

# Extract URLs from the articles
article_urls = extract_article_urls(article_html_array)

news_array = []

for url in article_urls:
    news_article = fetch_articles(url)  # Fetch and parse the article
    news_array.append(news_article)

# ----- add them to MongoDB -----

for news_article in news_array:
    collection.insert_one(news_article)

# Close the connection
client.close()