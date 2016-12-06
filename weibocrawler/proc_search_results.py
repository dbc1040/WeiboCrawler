# -*- coding: utf-8 -*-
#
# 1. Parse the data which is crawled by 'get_search_results.py'and stored in collection SearchPages.
# 2. Insert parser seed user data into collection Nicks.
#
# by doufunao
#
# 2014-03-15
#
import re
import json
from bs4 import BeautifulSoup
from weibocrawler import dboperator
from weibocrawler import log
import time


def content_html_parser(htmlbody):
	'''
	Usage:
			getContent(htmlbody)
					htmlbody not jsondata
			return htmlstr
	'''
	weibo_content_pattern = re.compile(r'<script>STK && STK\.pageletM && STK\.pageletM\.view\((\{\"pid\":\"pl_weibo_direct\".*?\})\)</script>')
	if weibo_content_pattern.search(htmlbody) != None:
		script_content = weibo_content_pattern.findall(htmlbody)[0]
	else:
		return 'Null'
	loadjson = json.loads(script_content)
	content = loadjson['html']
	return content


def nick_parser(content):
	soup = BeautifulSoup(content)
	# Attribute 'nick-name'&'usercard' exist
	result = soup.find_all("a", attrs={"nick-name": True, "usercard": True})
	nicklist = []
	for n in result:
		href = n['href']
		nick_name = n['nick-name']
		title = n['title']
		namedict = {}
		namedict['href'] = href
		namedict['nick-name'] = nick_name
		namedict['title'] = title
		nicklist.append(namedict)
	return nicklist

def convert_str_to_utf8(str):
	pattern_chinese_part_num = re.compile(r'\\u\w{4}')
	chinese_part_num = len(pattern_chinese_part_num.findall(str))
	str_ch = str
	Character = pattern_chinese_part_num.findall(str)
	for i in range(chinese_part_num):
		str_ch = str_ch.replace(Character[i], eval("u'" + Character[i] + "'"))
	return str_ch

def parse_weibo(weibo, keyword, dbo_SearchWeibo, pageIndex):

	soup_weibo = weibo

	soup_user_info = soup_weibo.find_all("a", class_='name_txt W_fb')
	str_user_info = str(soup_user_info)

	pattern_nick_name = re.compile('nick-name=".*?"')
	nick_name = ""
	try:
		nick_name = pattern_nick_name.findall(str_user_info)[0]
		# nick_name = convert_str_to_utf8(nick_name)
		nick_name = nick_name[11:-1]
	except Exception as ex:
		print(ex)

	pattern_user_homepage = re.compile('href=".*?"')
	user_homepage = ""
	try:
		user_homepage = pattern_user_homepage.findall(str_user_info)[0]
		user_homepage = user_homepage[6:-1]
	except Exception as ex:
		print(ex)

	soup_weibo_content = ""
	# class = comment_txt的<p>可以匹配到微博内容
	try:
		soup_weibo_content = soup_weibo.find_all("p", class_='comment_txt')[0]
		str_weibo_content = str(soup_weibo_content)
		# 去掉html标签
		pattern_weibo_content = re.compile('<[^>]+>')
		weibo_content = pattern_weibo_content.sub("", str_weibo_content)
		# weibo_content = convert_str_to_utf8(weibo_content)
	except Exception as ex:
		print(ex)

	soup_feed_from = ""
	# class = feed_from W_textb的<p>可以匹配到微博时间、网址、设备
	try:
		soup_feed_from = soup_weibo.find_all(
			"div", class_='feed_from W_textb')[0]
		str_feed_from = str(soup_feed_from)
	except Exception as ex:
		print(ex)

	weibo_time = ""
	pattern_time = re.compile('date=".*?"')
	try:
		weibo_time = pattern_time.findall(str_feed_from)[0]
		weibo_time = int(weibo_time[6:-1]) / 1000
		weibo_time = time.localtime(weibo_time)
		weibo_time = time.strftime('%Y-%m-%d %H:%M:%S', weibo_time)
	except Exception as ex:
		print(ex)

	pattern_weibo_href = re.compile('href=".*?"')
	weibo_href = ""
	try:
		weibo_href = pattern_weibo_href.findall(str_feed_from)[0]
		weibo_href = str(weibo_href)
		weibo_href = weibo_href[6:-1]
	except Exception as ex:
		print(ex)

	# 有的微博没有设备信息，sigh……
	weibo_target = ""
	try:
		weibo_target = soup_feed_from.find_all("a", target='_blank')[0]
		weibo_target = str(weibo_target)
		pattern_weibo_target = re.compile('<[^>]+>')
		weibo_target = pattern_weibo_target.sub("", weibo_target)
		# weibo_target = convert_str_to_utf8(weibo_target)
	except Exception as ex:
		print(ex)
		print(soup_feed_from)
		print(weibo_href)

	try:
		dbo_SearchWeibo.insert({"weibo_content": weibo_content, "nick_name": nick_name,
								"user_homepage": user_homepage, "weibo_time": weibo_time, "weibo_href": weibo_href,
								'weibo_target': weibo_target, "keyword": keyword, 'pageIndex': pageIndex})
	except Exception as ex:
		print(Exception)
		print(ex)
		print(weibo_href)
	return

# 从网页源码htmlStr中获取feed所在的<script>标签并提取html代码

def parse_search_pages(dbo_SearchPages, dbo_SearchWeibo):
	cursor = dbo_SearchPages.coll.find(
		{}, {'htmlStr': 1, 'pageUrl': 1, 'queryString': 1, 'pageIndex': 1})
	for c in cursor:
		_id = c['_id']
		htmlStr = c['htmlStr']
		pageUrl = c['pageUrl']
		keyword = c['queryString']
		# 如果dict中没有相关的值，上面的方法会报错
		pageIndex = c.get('pageIndex')
		str_weibo_search_feed = content_html_parser(htmlStr)
		if str_weibo_search_feed == 'Null':
			continue
		str_weibo_search_feed = str_weibo_search_feed[8: -3]
		str_weibo_search_feed = str_weibo_search_feed.replace('\\n', '\n')
		str_weibo_search_feed = str_weibo_search_feed.replace('\\t', '')
		str_weibo_search_feed = str_weibo_search_feed.replace('\\/', '/')
		str_weibo_search_feed = str_weibo_search_feed.replace('\\"', '"')

		soup_weibo = BeautifulSoup(str_weibo_search_feed)
		bs4_result_weibo = soup_weibo.find_all(
			"div", class_='WB_cardwrap S_bg2 clearfix')

		for weibo in bs4_result_weibo:
			parse_weibo(weibo, keyword, dbo_SearchWeibo, pageIndex)
	return


def main():
	from weibocrawler.config import getconfig
	cfg = getconfig()
	Collection_SearchPages = cfg['Collections']['SearchPages']
	Collection_SearchWeibo = cfg['Collections']['SearchWeibo']

	log('parse_search_pages', 'Running')

	dbo1 = dboperator.Dboperator(collname=Collection_SearchPages)
	dbo2 = dboperator.Dboperator(collname=Collection_SearchWeibo)
	parse_search_pages(dbo1, dbo2)
	dbo1.connclose()
	dbo2.connclose()
	log('parse_search_pages', 'Finished')
