# Importing requests library
import requests

# Defining target webpage to retrieve data
target = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
resp = requests.get(target)

# Importing Beautiful Soup library
from bs4 import BeautifulSoup
import bs4

# Retrieving the web page data in text format
soup = BeautifulSoup(resp.text, 'lxml')

# Using HTML tags, relevant data is fetched from the webpage
table = soup.find('table', {'id': 'constituents'})

# Getting table rows in the variable "rows"
rows = list(table.find_all('tr'))

all_tickers = []
# This for loop retrieves data from each and every row
# and saves the information for ticker, name of company, sector, URL
# in a dictionary named company
for row in rows[1:]:
    company = {}
    children = row.children
    children = [child for child in children if type(child) is bs4.element.Tag]
    company['ticker'] = children[0].get_text().strip()
    company['name'] = children[1].get_text()
    company['sector'] = children[3].get_text()
    company['quote_url'] = children[0].find('a')['href']
    all_tickers.append(company)
    
for ticker in all_tickers:
    if ticker['sector'] == 'Health Care':
        print(ticker['ticker'], ' | ', ticker['name'])

# Just for peeking in the retrieved data for a particular sector
all_health_care = [ ticker for ticker in all_tickers if ticker['sector'] == 'Health Care']
all_tech = [ ticker for ticker in all_tickers if ticker['sector'] == 'Information Technology']

# After retrieving the name of company and saving it to the list, I search on google
# for the news articles regarding those s&p 500 comopanies
search_target = "https://www.google.com/search?q={}+stock&safe=strict&tbm=nws&ei=Gb1VXfqNDc3UtQXFoL7oDQ&start={}&sa=N&ved=0ahUKEwi6_qel2IXkAhVNaq0KHUWQD90Q8tMDCF8&biw=1527&bih=739&dpr=1.1"

from bs4 import BeautifulSoup

# Getting news data from google search for the companies
def get_news_item(webpage_goog):
    target_div = 'g'
    soup = BeautifulSoup(webpage_goog, 'lxml')
    cards = soup.find_all('div', {'class': target_div}) #Returns a resultset
    #print('Found {} cards'.format(len(cards)))
    return list(cards)

# This function will clear the URL as there were some URL which required cleaning
def clean_google_url(dirty_url):
    return dirty_url.split('&sa')[0].split('q=')[1]

# Importing sentiment analyzer from Natural Language Toolkit
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Thus function gets the polarity score for every article found from the google search
def get_polarity_score(text):
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)['compound']


from newspaper import Article, ArticleException
def get_link_title_from_card(list_cards):
    all_links = []
    for item in list_cards:
        single_news = {}
        grab = list(item.findChildren('a'))[0]
        url = clean_google_url(grab['href'])
        print("Scrapping actual news from {}".format(url))
        single_news['url'] = url
        try:
            article = Article(url)
            article.download()
            article.parse()
            single_news['headline'] = article.title
            single_news['news_page'] = article.text
            single_news['authour'] = article.authors
            single_news['keywords'] = article.keywords
            single_news['date'] = article.published_date
            single_news['sentiment'] = get_polarity_score(article.text)
        except ArticleException as ae:
            print('Could not fetch article at {}'.format(url))
        all_links.append(single_news)
    return all_links

# This function is used to define proxy for article fetching from google search
# without any disruptions
def fetch_via_proxy(url):
    import time
    from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
    req_proxy = RequestProxy()
    request = req_proxy.generate_proxied_request(url)
    if request is not None:
        time.sleep(5)
        return request

import time
import random
all_scraped = {}
list_slice = all_tickers[:15]
for company in list_slice:
    scrape = []
    ticker = company['ticker']
    for page in range(0, 40, 10):
        ok = False
        while not ok:
            resp = requests.get(search_target.format(ticker, page))
            if resp: ok = resp.ok
            time.sleep(random.choice([1,2,3,4,5]))
        print('Scrapping headlines on page {} for {} on www.google.com'.format(int(page/10+1), ticker))
        scrape.extend(get_link_title_from_card(get_news_item(resp.text))) 
    all_scraped[ticker] = scrape
    percent_done = int((list_slice.index(company)+1)/len(list_slice) * 100) 
    print("We are {}% completed".format(round(percent_done, 2)))


mmm = all_scraped['MMM']
neg_news_mmm = [news for news in mmm if news['sentiment'] < 0]