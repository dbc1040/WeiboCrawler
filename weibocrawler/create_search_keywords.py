# -*- coding: utf-8 -*- 

from weibocrawler import dboperator

def create_SearchKeywords(file_name, dbo):
	fr = open(file_name, "r", encoding = "utf-8")
	for l in fr.readlines():
		keyword = l.strip()
		dbo.coll.update({'keyword': keyword},{'$set': {'keyword': keyword } }, upsert = True)
'''
This function will crawler user page read from collection Nicks and insert them into collection UserHomePages from MongoDB.
'''
def main():
	from weibocrawler.config import getconfig
	cfg = getconfig()
	file_name = "INPUT//SearchKeywords.txt"
	SearchKeywords = cfg['Collections']['SearchKeywords'] #"Nicks_iter02_10_06"# get href	
	dbo = dboperator.Dboperator(collname = SearchKeywords)
	create_SearchKeywords(file_name, dbo)
	dbo.connclose()

