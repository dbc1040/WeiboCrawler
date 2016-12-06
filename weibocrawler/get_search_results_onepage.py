#-*- coding:utf8 -*-
from weibocrawler import log
from weibocrawler import dboperator
from weibocrawler import WeiboHttpRequest
from weibocrawler import WeiboLogin
import urllib.parse
import time
import random
import re
import json
import datetime
from bs4 import BeautifulSoup
from weibocrawler.convert_cookies import convert_cookies
from weibocrawler.config import getconfig

cfg1 = getconfig()
KeywordSleeptime = int(cfg1['CrawlParameter']['KeywordSleeptime'])

def get_request(check_cookie_file=True):
    '''get a weibo http request'''
    username = '1111111111111'
    password = '1111111111111'
    if check_cookie_file == True:
        convert_cookies()
    login = WeiboLogin(username, password)
    http_request = WeiboHttpRequest(login)
    return http_request

def crawler_pages(http_request, dbo1, dbo2):
	cursor = dbo2.coll.find({}, {'keyword': 1, 'keywordcrawled': 1})
	for c in cursor:
		if int(c.get("keywordcrawled",0)) == 1:
			continue
		else:
			sp = {}
			timebatch = str(datetime.datetime.now().strftime("%Y%m%d%H%M"))
			sp['timebatch'] = timebatch
			queryString = c['keyword']
			log('Begin to get', queryString)
			page_tuple = __crawler_each_page(http_request, queryString)
			urlstr = page_tuple[0]
			htmlstr = page_tuple[1]

			sp['pageurl'] = urlstr
			sp['htmlstr'] = htmlstr
			sp['crawlertime'] = datetime.datetime.now().timestamp()
			sp['querystring'] = queryString
			dbo1.insert(sp)
			dbo2.coll.update({'keyword': queryString}, {'$set': {'keywordcrawled': 1}}, multi=True)
			log("crawler Page finished:",queryString)
	log("crawler all Page:","finished!")


def __crawler_each_page(http_request, queryString, page_num = 1):
    '''only one page at a time'''
    sleeptime = random.randint(KeywordSleeptime, KeywordSleeptime+5)
    log('crawler_each_page sleep time', str(sleeptime))
    time.sleep(sleeptime)

    url_str = 'http://s.weibo.com/weibo/' + \
        urllib.parse.quote(queryString) + '&page=' + str(page_num)
    htmlstr = http_request.get(url_str)
    return (url_str, htmlstr)


def main(http_request = ""):
	'''
	This function will crawler search page of weibo and write them into MongoDB.
	Usage:
	'''
	from weibocrawler.config import getconfig
	cfg = getconfig()
	Collection_SearchPages = cfg['Collections']['SearchPages']
	Collection_SearchKeywords = cfg['Collections']['SearchKeywords']
	dbo1 = dboperator.Dboperator(collname=Collection_SearchPages)  # use config infor
	dbo2 = dboperator.Dboperator(collname=Collection_SearchKeywords)  # use config info
	if http_request == '':
		http_request = get_request()
	crawler_pages(http_request, dbo1, dbo2)
