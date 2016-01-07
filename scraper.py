# coding=utf-8
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
import threading
import datetime

##
# Setup
##
time = 30 #schedule time

client = MongoClient('localhost', 27017)
db = client.pypaper_api #name of db

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
	date = datetime.datetime.now()
	#parse url
	req = requests.get(url.get('link'), headers=request_headers)
	soup = BeautifulSoup(req.content, 'xml')

	for item in soup.findAll('item')[0:3]:
		article = {}
		article['title'] = item.title.text.encode('utf-8')
		if collection.find({'title':article.get('title')}).count() == 0:

			article['link'] = item.link.text.encode('utf-8')
			article['pubdate'] =  date.isoformat()
			article['provider'] = url.get('provider')
			article['country'] = url.get('country')
			article['category'] = url.get('category')
			try:
				article['tag'] = item.category.text.encode('utf-8')
			except:
				article['tag'] = ""
			try:
				article['image_url'] =  item.image.url.text.encode('utf-8')
			except Exception as e:
				article['image_url'] =  get_image(item.link.text.encode('utf-8')) or ""

			article['_id'] = getNextId()
			collection.insert(article)
			print article.get('title')

###
# Open file
# @return urls
###
def get_urls():
	urls = []
	"""
	#opening links from txt file
	with open('scripts/parser/urls.txt', 'r') as file:
		for line in file:
			urls.append(line[:line.find('\n')])
	"""
	url_db = db['urls']
	#GET urls from db
	for url in url_db.find({}):
		urls.append(url)
	return urls


##
# schedules a timer on seperate thread
# parsing each url returned from get_urls()
##
def schedule():
	for url in get_urls():
		#print 'parsing url: ', url
		try:
			parse(url)
		except Exception as e:
			print e
	threading.Timer(time, schedule).start()

if __name__ == '__main__':
	schedule()
