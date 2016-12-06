#
# 1. Crawl the user timeline pages using the pageid get from collection UserHomePages
# 2. Insert the timeline pages into collection TimelinePages
#
# doufunao
# 2014-08-11
#

from weibocrawler import log
from weibocrawler import dboperator
from weibocrawler import weibo_struct
from weibocrawler import WeiboHttpRequest
from weibocrawler import WeiboLogin
import time
import math
import random
import datetime
from weibocrawler.convert_cookies import convert_cookies
from weibocrawler.config import getconfig

cfg1 = getconfig()
UserWeiboSleeptime = int(cfg1['CrawlParameter']['UserWeiboSleeptime'])

def get_request(check_cookie_file = True):
	username = '1111111111111'
	password = '1111111111111'
	if check_cookie_file == True:
		convert_cookies()
	login = WeiboLogin(username, password)
	http_request = WeiboHttpRequest(login)
	return http_request

def get_domain(pageid, userid):
	return pageid.replace(userid, '')
	
def __crawl_each_timeline_page(http_request, para_dict):
	sleeptime = random.randint(UserWeiboSleeptime,UserWeiboSleeptime+5)
	log('Ready to get each json data. Just have a rest', 'sleeptime: ' + str(sleeptime))
	time.sleep(sleeptime)		
	json_urlstr = 'http://weibo.com/p/aj/mblog/mbloglist?domain=%(domain)s&pre_page=%(prePage)s&page=%(page)s&pagebar=%(pageBar)s&id=%(pageId)s' % (para_dict)
	jsonstr = http_request.get(json_urlstr)
	para_dict['pageUrl'] = json_urlstr
	para_dict['htmlStr'] = jsonstr
	returndic = {}
	returndic.update(para_dict)
	return returndic
def update_dbo_userpages(dbo_userpages, userid, page):
	dbo_userpages.coll.update({'userId': userid} ,{'$set': {'last_page': page } }, multi = True)
def update_dbo_timelinepages(dbo_timelinepages,timelinedict):
	timebatch = datetime.datetime.now().timestamp()
	timelinedict['timeBatch'] = timebatch
	dbo_timelinepages.coll.insert(timelinedict)
def crawl_timeline_pages(http_request, userid, pageid, end_page_num,dbo_userpages,dbo_timelinepages,begin_page_number):
	'''
	输入：获得cookie的request、pageId、end_page_num
	输出：此人的前五页timeline内容
	'''
	para_dict = {}
	para_dict['prePage'] = 0
	para_dict['page'] = 1 # page number
	para_dict['pageBar'] = 0 # section number
	para_dict['pageId'] = pageid
	para_dict['userId'] = userid
	para_dict['domain'] = get_domain(pageid, userid)
	for page in range(begin_page_number, end_page_num):
		#url para : page_id = default, page = page, pre_page = 0, pagebar = 0
		para_dict['page'] = page
		para_dict['prePage'] = 0
		para_dict['pageBar'] = 0
		para_dict['crawlerTime'] = datetime.datetime.now().timestamp()
		new_dict = __crawl_each_timeline_page(http_request, para_dict)
		update_dbo_timelinepages(dbo_timelinepages,new_dict)
		# user_timeline_pages.append()
		#url para : page_id = default, page = page, pre_page = page, pagebar = 0
		para_dict['prePage'] = page
		para_dict['crawlerTime'] = datetime.datetime.now().timestamp()
		new_dict = __crawl_each_timeline_page(http_request, para_dict)
		update_dbo_timelinepages(dbo_timelinepages,new_dict)

		#url para : page_id = default, page = page, pre_page = page, pagebar = 1
		para_dict['pageBar'] = 1
		para_dict['crawlerTime'] = datetime.datetime.now().timestamp()
		#log('Url para','Page: ' + str(page) + ' len(jsondata[\'timeline_page\']) : ' + str(len(jsondata['timeline_page'])))
		new_dict = __crawl_each_timeline_page(http_request, para_dict)
		update_dbo_timelinepages(dbo_timelinepages,new_dict)

		update_dbo_userpages(dbo_userpages, userid, page)
	
def cal_page_num(weibonum, page_num_upper_bound):
	end_page_num = math.ceil(int(weibonum) / 45) + 1
	if end_page_num > page_num_upper_bound:
		end_page_num = page_num_upper_bound + 1
	return end_page_num

def get_user_timeline_pages(http_request, dbo_userpages, dbo_timelinepages, page_num_upper_bound = 10):
	'''one page one document'''
	dbo1 = dbo_userpages
	dbo2 = dbo_timelinepages
	# pid_cursor = dbo1.coll.find({'userId': '1088602681'},{'timelineCrawled': 1, 'pageId': 1, 'userId': 1, 'weiboNum': 1})
	pid_cursor = dbo1.coll.find({},{'timelineCrawled': 1, 'pageId': 1, 'userId': 1, 'weiboNum': 1,'last_page':1}, timeout = False)

	pid_list = list(pid_cursor)
	timebatch = datetime.datetime.now().timestamp()
	for user in pid_list:
		_id = user['_id']
		userid = user['userId']
		pageid = user['pageId']
		weibonum = int(user.get('weiboNum', -1))
		last_page = int(user.get('last_page', 1))
		crawled = int(user.get('timelineCrawled', 0))
		if crawled == 1:
			continue
		if pageid == -1 or pageid == '':
			continue
		if weibonum == -1:
			continue
		begin_page_number = last_page
		end_page_num = cal_page_num(weibonum, page_num_upper_bound) # get the first 10 timeline page
		log('begin', 'userid ' + str(userid) + ' weibonum ' + str(weibonum) + ' end page '+ str(end_page_num))
		crawl_timeline_pages(http_request, userid, pageid, end_page_num,dbo1,dbo2,begin_page_number)

		dbo1.coll.update({'userId': userid} ,{'$set': {'timelineCrawled': 1 } }, multi = True)
		log('get_user_timeline_pages', 'userid: ' + str(userid) + ' pageid: ' + str(pageid))

def main(http_request = ""):
	cfg = getconfig()
	Collection_UserHomePages = cfg['Collections']['UserHomePages']
	Collection_UserTimelinePages = cfg['Collections']['UserTimelinePages']
	dbo1 = dboperator.Dboperator(collname = Collection_UserHomePages)
	dbo2 = dboperator.Dboperator(collname = Collection_UserTimelinePages)
	# dbo1 = dboperator.Dboperator(collname = 'UserHomePages')
	# dbo2 = dboperator.Dboperator(collname = 'UserTimelinePages')
	if http_request == "":
		http_request = get_request()
	UserWeiboPages = int(cfg['CrawlParameter']['UserWeiboPages'])
	get_user_timeline_pages(http_request, dbo1, dbo2, page_num_upper_bound = UserWeiboPages)
	dbo1.connclose()
	dbo2.connclose()