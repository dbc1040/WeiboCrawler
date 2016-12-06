# -*- coding: utf-8 -*-
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
	weibo_content_pattern = re.compile(r'<script>STK && STK\.pageletM && STK\.pageletM\.view\((\{\"pid\":\"pl_weibo_directtop\".*?\})\)</script>')
	if weibo_content_pattern.search(htmlbody) != None:
		script_content = weibo_content_pattern.findall(htmlbody)[0]
	else:
		return 'Null'
	loadjson = json.loads(script_content)
	content = loadjson['html']
	return content

def parse_search_pages(dbo_SearchPages):
	cursor = dbo_SearchPages.coll.find(
		{}, {'htmlstr': 1, 'querystring': 1})
	for c in cursor:
		_id = c['_id']
		htmlStr = c['htmlstr']
		keyword = c['querystring']
		str_weibo_search_feed = content_html_parser(htmlStr)
		if str_weibo_search_feed == 'Null':
			user_href = 'Null'
			dbo_SearchPages.coll.update({'querystring': keyword}, {'$set': {'user_href': user_href}}, multi=True)
			continue
		str_weibo_search_feed = str_weibo_search_feed[8: -3]
		str_weibo_search_feed = str_weibo_search_feed.replace('\\n', '\n')
		str_weibo_search_feed = str_weibo_search_feed.replace('\\t', '')
		str_weibo_search_feed = str_weibo_search_feed.replace('\\/', '/')
		str_weibo_search_feed = str_weibo_search_feed.replace('\\"', '"')

		soup_weibo = BeautifulSoup(str_weibo_search_feed)
		bs4_result_weibo = soup_weibo.find(
			"a",{'suda-data':'key=tblog_search_weibo&value=direct_user_icon'})
		# print(bs4_result_weibo)
		if bs4_result_weibo == None:
			continue
		user_href = bs4_result_weibo.get('href','')
		if user_href == '':
			continue
		user_href = user_href[:user_href.find('?')]
		print(user_href)
		dbo_SearchPages.coll.update({'querystring': keyword}, {'$set': {'user_href': user_href}}, multi=True)
	return

def main():
	from weibocrawler.config import getconfig
	cfg = getconfig()
	Collection_SearchPages = cfg['Collections']['SearchPages']
	log('parse_search_pages', 'Running')

	dbo1 = dboperator.Dboperator(collname=Collection_SearchPages)
	parse_search_pages(dbo1)
	dbo1.connclose()
	log('parse_search_pages', 'Finished')
