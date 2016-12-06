# import weibocrawler
from weibocrawler import log
from weibocrawler import dboperator
from weibocrawler import weibo_struct
from weibocrawler import WeiboHttpRequest
from weibocrawler import WeiboLogin
import sys
import time
import random
import datetime
from weibocrawler.convert_cookies import convert_cookies
from weibocrawler.config import getconfig

cfg1 = getconfig()
UserPagesSleeptime = int(cfg1['CrawlParameter']['UserPagesSleeptime'])

def get_request(check_cookie_file = True):
	username = '1111111111111'
	password = '111111111111'
	if check_cookie_file == True:
		convert_cookies()
	login = WeiboLogin(username, password)
	http_request = WeiboHttpRequest(login)
	return http_request

def __crawler_each_page(http_request, url):
	sleeptime = random.randint(UserPagesSleeptime,UserPagesSleeptime + 5)
	log('crawler_each_page sleep time', str(sleeptime))
	time.sleep(sleeptime)
	htmlstr = http_request.get(url)
	return htmlstr

def get_user_home_pages(http_request, dbo_userpages, dbo_userclawer):
	# up = weibo_struct.UserHomePage()
	urls = dbo_userclawer.coll.find({},{'crawled': 1, 'href': 1},timeout=False)
	# urls = dbo_userclawer.coll.find({'href': 'http://weibo.com/u/3867395827'},{'crawled': 1, 'href': 1})
	timebatch = datetime.datetime.now().timestamp()
	for url in urls:
		if int(url.get('crawled', 0)) == 1:
			continue
		else:
			pagedic = {}
			pagedic['pageId'] = -1
			pagedic['userId'] = -1
			pagedic['nickName'] = ''
			pagedic['pageUrl'] = url['href']
			pagedic['nickId'] = url['_id']
			pagedic['timeBatch'] = timebatch
			# print(pagedic)
			# sys.exit()
			htmlstr = __crawler_each_page(http_request, url['href'])
			pagedic['htmlStr'] = htmlstr
			pagedic['crawlerTime'] = datetime.datetime.now().timestamp()

			dbo_userpages.coll.update({'href': pagedic['pageUrl']},{'$set': pagedic}, upsert = True)
			dbo_userclawer.coll.update({'href': url['href']} ,{'$set': {'crawled': 1 } }, multi = True)
			log('got user home pages', url['href'])

def get_user_home_pages_entry(http_request = ""):
	'''
	This function will crawler user page read from collection Nicks and insert them into collection UserHomePages from MongoDB.
	'''
	cfg = getconfig()
	Collection_Nicks = cfg['Collections']['Nicks'] # get href	
	Collection_UserHomePages = cfg['Collections']['UserHomePages']

	# dbo1 = dboperator.Dboperator(collname = 'UserHomePages') # store: screen_name, page_id, user_id, htmlStr 
	# dbo2 = dboperator.Dboperator(collname = 'Nicks')
	dbo1 = dboperator.Dboperator(collname = Collection_UserHomePages) # store: screen_name, page_id, user_id, htmlStr 
	dbo2 = dboperator.Dboperator(collname = Collection_Nicks)
	if http_request == "":
		http_request = get_request()
	get_user_home_pages(http_request, dbo1, dbo2)
	dbo1.connclose()
	dbo2.connclose()

