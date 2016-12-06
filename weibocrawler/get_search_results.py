#-*- coding:utf8 -*-
from weibocrawler import log
from weibocrawler import dboperator
from weibocrawler import weibo_struct
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


def findSearchNum(content):
	# f = open('1.txt',"w",encoding='utf-8')
	# f.write(content)
	# f.close()
	search_num_pattern = re.compile(r'<span>\\u627e\\u5230(.*?)\\u6761\\u7ed3\\u679c\\uff0c<\\/span>')
	if search_num_pattern.search(content) != None:
		search_num = int(search_num_pattern.findall(content)[0])
		# print(search_num)
		return search_num
	else:
		return 0

def crawler_pages(http_request, dbo1, dbo2, queryStrings, end_num_input=0):
	cursor = dbo2.coll.find({}, {'keyword': 1, 'page2crawle': 1, 'keywordcrawled': 1})
	for c in cursor:
		if int(c.get("keywordcrawled",0)) == 1:
			continue
		else:
			start_num = int(c.get('page2crawle',1))
			sp = weibo_struct.SearchPage()
			timebatch = str(datetime.datetime.now().strftime("%Y%m%d%H%M"))
			sp.timebatch = timebatch
			end_num = end_num_input
			queryString = c['keyword']
			log('Begin to get', queryString)
			page_tuple = __crawler_each_page(http_request, queryString, start_num)
			urlstr = page_tuple[0]
			htmlstr = page_tuple[1]

			search_num = findSearchNum(htmlstr)

			sp.pageurl = urlstr
			sp.htmlstr = htmlstr
			sp.pageindex = start_num
			sp.crawlertime = datetime.datetime.now().timestamp()

			if search_num == 0:
				log('crawlerPage says: No search result' +str(queryString), 'search_num == 0')
				continue
			else:
				if end_num == 0:
					end_num = int(search_num / 20)
					end_num = end_num + 1
					if end_num > 5:
						end_num = 5

			log(' '.join(['\n', 'crawler_pages', str(end_num), 'pages']), ' '.join(
				['Got', queryString, 'search_num', str(search_num), '\n']))

			sp.resulttotal = search_num
			sp.querystring = queryString
			sp.pagetotal = end_num
			pagedict = sp.getdict()
			dbo1.insert(pagedict)

			for x in range(start_num + 1, end_num + 1):
				page_tuple = __crawler_each_page(http_request, queryString, x)
				urlstr = page_tuple[0]
				htmlstr = page_tuple[1]
				sp.pageurl = urlstr
				sp.htmlstr = htmlstr
				sp.pageindex = x
				sp.crawlertime = datetime.datetime.now().timestamp()
				pagedict = sp.getdict()
				dbo1.insert(pagedict)
				dbo2.coll.update({'keyword': queryString}, {'$set': {'page2crawle': x + 1}}, multi=True)

			dbo2.coll.update({'keyword': queryString}, {'$set': {'keywordcrawled': 1}}, multi=True)
			end_num = end_num_input
			log("crawler Page finished:",queryString)
	log("crawler all Page:","finished!")


def __crawler_each_page(http_request, queryString, page_num):
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
	KeywordWeiboPages = int(cfg["CrawlParameter"]["KeywordWeiboPages"])
	crawler_pages(http_request, dbo1, dbo2, KeywordWeiboPages)
