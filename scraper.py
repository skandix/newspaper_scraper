# coding=utf-8
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import threading

##
# Setup
##
time = 15 #schedule time

client = MongoClient('localhost', 27017)
db = client.newspaper

try:
    collection = db.create_collection('articles', capped = True, max = 3000, size = 5242880)
except:
    collection = db['articles']

request_headers = {
"Accept-Language": "en-US,en;q=0.5",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
"Content-Type":"Text",
"Connection": "keep-alive"
}

#This method is used to generate an id for the article (newest articles gets higher number)
def getNextId():
    try:
        res = db.counters.find_and_modify(
            query={ '_id' : 'id' },
            update={'$inc': {'seq': 1}},
            new=True
        ).get('seq')
        return res
    except:
        db.counters.insert({'_id':'id', 'seq':0})
        return 0
##
# Get image from article url inside og:image meta
##
def get_image(url):
    req = requests.get(url, headers=request_headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    try:
        image_meta = soup.find(property = 'og:image') or soup.find(name = 'twitter:image')
        return image_meta.get('content')
    except:
        image_meta = ""
        return image_meta

###
# Parse each xml url get content
# Connects to mongodb and inserts article dicitonary if not exists
###
def parse(url):
    provider = url[url.find('.') + 1:]
    provider = provider[:provider.find('/')]

    #parse url
    req = requests.get(url, headers=request_headers)
    soup = BeautifulSoup(req.content, 'xml')

    for item in soup.findAll('item')[0:3]:
        article = {}

        article['title'] = item.title.text.encode('utf-8')
        #article['description'] = item.description.text.encode('utf-8')
        article['link'] = item.link.text.encode('utf-8')
        article['pubdate'] = item.pubDate.text.encode('utf-8')
        article['provider'] = provider
        try:
            article['category'] = item.category.text.encode('utf-8')
        except:
            article['category'] = ""
        try:
            article['image_url'] =  item.image.url.text.encode('utf-8')
        except Exception as e:
            article['image_url'] =  get_image(item.link.text)

        if collection.find({'title':article.get('title')}).count() == 0:
            article['_id'] = getNextId()
            collection.insert(article)
            #print article

###
# Open file
# @return urls
###
def get_urls():
    urls = []
    with open('urls.txt', 'r') as file:
        for line in file:
            urls.append(line[:line.find('\n')])
    return urls

##
# schedules a timer on seperate thread
# parsing each url returned from get_urls()
##
def schedule():
    for url in get_urls():
        print 'parsing url: ', url
        parse(url)
    print "-------------------------------"
    threading.Timer(time, schedule).start()

if __name__ == '__main__':
    schedule()
