from newsapi import NewsApiClient
import json

# Init
newsapi = NewsApiClient(api_key='d3457d8fe19a4920951fe84602a82fce')

# Fetch all sources
all_sources = newsapi.get_sources()

# Filter for the desired sources
desired_sources = ['spacenews.com', 'sciencealert.com', 'motorsport.com', 'theverge.com']
found_sources = {}

for source in all_sources['sources']:
    if source['url'] in desired_sources:
        found_sources[source['id']] = source['name']
        

# Print the found source IDs and names
print(json.dumps(found_sources, indent=2))