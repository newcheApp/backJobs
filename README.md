# backJobs
Back jobs for web Scrapping creating summary and tags.

main_backjobs.py are using to automating all the steps. 
New news are added to unprocessed news in db for not showing users news without tag and summary.

## Web Scraping
- Uses RSS feeds of the news website for get latest news.
- Checks that the news are already in database.
- Identifys the ones not in DB and start barcing their content in URLs that are privided from RSS feed.
- full body, date, url, first image, and title are added to the database

## Summary Generation
- Title and bodies fed to the news summarizer and added to those news.
- news summaries generated added to the database.

## Tag generation
- summaries and title fed to the Chat GPT with specific Prompt for generating tags
- tag names are check for are they still existing in DB. If yes it takes tags object id adds to news. If not new tag generated.

