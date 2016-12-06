 #-*- coding:utf8 -*-
#
# Parse the data which 'get_user_pages.py' crawled and is stored in collection UserHomePages.
# Upate collection UserHomePages with new parsed data.
# doufunao
#
# 2014-08-11

import re
from weibocrawler import dboperator
from weibocrawler import log
import os
from weibocrawler import WeiboHttpRequest
from weibocrawler import WeiboLogin
from weibocrawler import log
import sys
import time
import random
import datetime
from weibocrawler.convert_cookies import convert_cookies
from weibocrawler.config import getconfig

cfg1 = getconfig()
UserinfoSleeptime = int(cfg1['CrawlParameter']['UserinfoSleeptime'])


def get_request(check_cookie_file = True):
	username = 'e1441430@drdrb.com'
	password = 'e1441430'
	if check_cookie_file == True:
		convert_cookies()
	login = WeiboLogin(username, password)
	http_request = WeiboHttpRequest(login)
	return http_request

def userinfo_parser(html_str):
	user_dict = {}
	pattern_uid = re.compile(r'\[\'oid\'\]=\'(\d+?)\'')
	pattern_nickname = re.compile(r'\[\'onick\'\]=\'(.+?)\'')
	pattern_page_id = re.compile(r'\[\'page_id\'\]=\'(.+?)\'')
	
	if pattern_page_id.search(html_str) != None:
		user_dict['user_id'] = pattern_uid.findall(html_str)[0]
		user_dict['screen_name'] = pattern_nickname.findall(html_str)[0]
		user_dict['page_id'] = pattern_page_id.findall(html_str)[0]

	else:
		user_dict['user_id'] = -1
		user_dict['screen_name'] = "None"
		user_dict['page_id'] = -1
	
	return user_dict
	
def parse_user_base_infos(dbo_userpages):
	cursor = dbo_userpages.coll.find({}, {'htmlStr': 1, 'pageUrl': 1})
	for c in cursor:
		_id = c['_id']
		htmlStr = c['htmlStr']
		pageUrl = c['pageUrl']
		ud = userinfo_parser(htmlStr)
		nickName = ud['screen_name']
		pageId = ud['page_id']
		userId = ud['user_id']
		dbo_userpages.coll.update({'_id': _id} ,{'$set': {'userId': userId, 'pageId': pageId, 'nickName': nickName} }, multi = True)
		if pageId == -1:
			print(pageUrl)
	return
def find_num(pattern, htmlstr):
	s1 = set(pattern.findall(htmlstr)[0])
	# print(pattern.findall(htmlstr)[0])
	s2 = set([''])
	num = list(s1-s2)
	return num[0]
def parse_introduction(pattern_introduction, htmlStr):
	str = pattern_introduction.findall(htmlStr)[0].strip()
	str = str.replace('\\t','').replace(' ','')
	# print (isinstance(str,unicode))
	str = str.encode('utf-8','ignore').decode('utf-8','ignore')
	# print (str)
	return str
def relation_parser(htmlStr):
	user_dict = {}
	user_dict['follower_num'] = -1
	user_dict['followee_num'] = -1
	user_dict['weibo_num'] = -1 
	# user_dict['introduction'] = 'None'

	pattern_follower_num = re.compile(r'<strong class=\\+"W_f18\\+">([\d\s]+?)<\\+/strong><span class=\\+"S_txt2\\+">Follow<\\+/span>|<strong node-type=\\"fans\\">([\d\s]+?)<\\/strong>|<strong class=\\+"W_f20\\+">([\d\s]+?)<\\+/strong><span>粉丝<\\/span>|<strong class=\\+"\\+">([\d\s]+?)<\\+/strong><span>粉丝<\\+/span>|<strong class=\\"W_f1[8642]\\">([\d\s]+?)<\\/strong><span class=\\"S_txt2\\">粉丝<\\/span>')
	pattern_followee_num = re.compile(r'<strong class=\\+"W_f18\\">([\d\s]+?)<\\+/strong><span class=\\+"S_txt2\\+">Followers<\\+/span>|<strong node-type=\\"follow\\">([\d\s]+?)<\\/strong>|<strong class=\\+"W_f20\\+">([\d\s]+?)<\\+/strong><span>关注<\\/span>|<strong class=\\+"\\+">([\d\s]+?)<\\+/strong><span>关注<\\+/span>|<strong class=\\"W_f1[8642]\\">([\d\s]+?)<\\/strong><span class=\\"S_txt2\\">关注<\\/span>')
	pattern_weibo_num = re.compile(r'<strong class=\\+"W_f18\\+">([\d\s]+?)<\\+/strong><span class=\\+"S_txt2\\+">Weibo<\\+/span>|<strong node-type=\\"weibo\\">([\d\s]+?)<\\/strong>|<strong class=\\+"W_f20\\+">([\d\s]+?)<\\+/strong><span>微博<\\/span>|<strong class=\\+"\\+">([\d\s]+?)<\\+/strong><span>微博<\\+/span>|<strong class=\\"W_f1[8642]\\">([\d\s]+?)<\\/strong><span class=\\"S_txt2\\">微博<\\/span>')
	# pattern_introduction = re.compile(r'<span class=\\+"item_text W_fl\\+">\\r\\n    \\t\\t\\t\\t\\t\\t    \\t\\t\\t\\t\\t\\t    \\t\\t\\t\\t\\t\\t(简介：.*?)<\\+/span>')

	if pattern_follower_num.search(htmlStr) != None:
		user_dict['follower_num'] = find_num(pattern_follower_num, htmlStr)

	if pattern_followee_num.search(htmlStr) != None:
		user_dict['followee_num'] = find_num(pattern_followee_num, htmlStr)

	if pattern_weibo_num.search(htmlStr) != None:
		user_dict['weibo_num'] = find_num(pattern_weibo_num, htmlStr)

	# if pattern_introduction.search(htmlStr) != None:
	# 	# print (pattern_introduction)
	# 	user_dict['introduction'] = parse_introduction(pattern_introduction, htmlStr)
	# 	# try:
	# 	# 	print (user_dict['introduction'])
	# 	# except Exception:
	# 	# 	print('有非法字符\n')

	return user_dict
	
def parse_user_relation(dbo_userpages):
	cursor = dbo_userpages.coll.find({}, {'htmlStr': 1, 'pageUrl': 1})
	for c in cursor:
		_id = c['_id']
		# pageurl = c['pageUrl']
		htmlstr = c['htmlStr']
		if htmlstr =='':
			continue
		else:
			ud = relation_parser(htmlstr)
		follower_num = ud['follower_num']
		followee_num = ud['followee_num']
		weibo_num = ud['weibo_num']
		# introduction = ud['introduction']
		if follower_num == -1 or followee_num == -1 or weibo_num == -1:			
			# print(pageurl)
			# print(re.search('抱歉，', htmlstr))
			continue
		dbo_userpages.coll.update({'_id': _id} ,{'$set': {'followerNum': follower_num, 'followeeNum': followee_num, 'weiboNum': weibo_num} }, multi = True)
	return

def __crawler_each_page(http_request, url):
	sleeptime = random.randint(UserinfoSleeptime,UserinfoSleeptime+5)
	log('crawler_each_page sleep time', str(sleeptime))
	time.sleep(sleeptime)
	htmlstr = http_request.get(url)
	return htmlstr

def parse_basic_information(htmlStr):
	user_dict = {}
	user_dict['address'] = 'None'
	user_dict['gender'] = 'None'
	user_dict['birthday'] = 'None'
	user_dict['introduction'] = 'None'
	user_dict['registrationDate'] = 'None'
	pattern_address = re.compile(r'<span class=\\+"pt_title S_txt2\\+">所在地：<\\+/span><span class=\\+"pt_detail\\+">(.*?)<\\+/span>')
	pattern_gender = re.compile(r'<span class=\\+"pt_title S_txt2\\+">性别：<\\+/span><span class=\\+"pt_detail\\+">(男|女)<\\+/span>')
	pattern_birthday = re.compile(r'<span class=\\+"pt_title S_txt2\\+">生日：<\\+/span><span class=\\+"pt_detail\\+">(.*?)<\\+/span>')
	pattern_introduction = re.compile(r'<span class=\\+"pt_title S_txt2\\+">简介：<\\+/span>\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t<span class=\\"pt_detail\\">(.*?)<\\/span>')
	pattern_registrationDate = re.compile(r'<span class=\\"pt_title S_txt2\\">注册时间：<\\/span>\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t<span class=\\"pt_detail\\">\\r\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t(.*?)\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t<\\/span>')

	if pattern_address.search(htmlStr) != None:
		user_dict['address'] = pattern_address.findall(htmlStr)[0].strip()
	if pattern_gender.search(htmlStr) != None:
		user_dict['gender'] = pattern_gender.findall(htmlStr)[0].strip()
	if pattern_birthday.search(htmlStr) != None:
		user_dict['birthday'] = pattern_birthday.findall(htmlStr)[0].strip()
	if pattern_introduction.search(htmlStr) != None:
		user_dict['introduction'] = pattern_introduction.findall(htmlStr)[0].strip()
	if pattern_registrationDate.search(htmlStr) != None:
		user_dict['registrationDate'] = pattern_registrationDate.findall(htmlStr)[0].strip()

	return user_dict

def get_user_basic_information(http_request,dbo):
	cursors = dbo.coll.find({},{'pageId': 1,'basic_information_crawled':1},timeout=False)
	count = 0
	for cursor in cursors:
		count += 1
		# basic_information_crawled = cursor['basic_information_crawled']
		if int(cursor.get('basic_information_crawled', 0)) == 1:
			continue
		pageId = cursor['pageId']
		if pageId == -1:
			continue
		else:
			basic_information_url = 'http://weibo.com/p/' + cursor['pageId'] + '/info?mod=pedit_more'
			basic_information_htmlstr = __crawler_each_page(http_request, basic_information_url)
			ud = parse_basic_information(basic_information_htmlstr)
			# print ('第'+str(count)+'个,'+'pageId:'+str(pageId))
			# a = input()
			address = ud['address']
			gender = ud['gender']
			birthday = ud['birthday']
			introduction = ud['introduction']
			registrationDate = ud['registrationDate']
			# basic_information_crawled = 1

			dbo.coll.update({'pageId': pageId} ,{'$set': {'address': address, 'gender': gender, 'birthday': birthday,'introduction':introduction,'registrationDate':registrationDate,'basic_information_url':basic_information_url,'basic_information_htmlstr':basic_information_htmlstr,'basic_information_crawled':1} }, multi = True)
	return

def proc_user_pages_entry(http_request = ""):
	cfg = getconfig()
	Collection_UserHomePages = cfg['Collections']['UserHomePages']
	# dbo = dboperator.Dboperator(collname = 'UserHomePages')
	dbo = dboperator.Dboperator(collname = Collection_UserHomePages)
	if http_request == "":
		http_request = get_request()

	log('parse_user_base_infos', 'Running')	
	parse_user_base_infos(dbo)
	log('parse_user_base_infos', 'Finished')

	log('parse_user_relation', 'Running')
	parse_user_relation(dbo)
	log('parse_user_relation', 'Finished')

	# log('get_user_basic_information', 'Running')	
	# get_user_basic_information(http_request,dbo)
	# log('get_user_basic_information', 'Finished')

	dbo.connclose()
