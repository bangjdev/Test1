# HEKATEAI - OA - Books data scraping
First programming test for a data science internship at HekateAI, crawling data from a books website goodreads.com
Given the link to a list of all books by an author, crawl all the books' info, reviews, rating, etc...

## </> DEPENDENCIES INSTALLATION
```
pip install -r requirements.txt
```
## </> RUN
#### To run the crawler, use this command from command line
```
scrapy crawl goodreads -o <output file>
```
#### For example
```
scrapy crawl goodreads -o results.json
```
## </> NOTES
By default, all logging information is stored in ```logs.txt``` file.
Every configuration is configured in the ```settings.py``` file, for example
- ```LOG_LEVEL = 'DEBUG'``` *the level of logging information*
- ```LOG_FILE = 'logs.txt'``` *default log file*
- ```RETRY_TIMES = 100``` *maximum number of retries if a request fails*
- ```TARGET_URLS = []``` *you can change or add the urls you want to scrape here*