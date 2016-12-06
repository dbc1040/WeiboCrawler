#coding:utf-8
from weibocrawler import dboperator
from weibocrawler import DirOperator
from weibocrawler.config import getconfig
import csv
def output_user_information(dbo,output_filename):
	csvfile = open(output_filename,'w',newline="")
	writer = csv.writer(csvfile,dialect='excel')
	writer.writerow(['关键词', '用户昵称', '用户主页','微博链接','微博内容','微博时间'])

	cursor = dbo.coll.find({},{"keyword":1,"nick_name":1,"user_homepage":1,\
		"weibo_href": 1,'weibo_content':1,'weibo_time':1})
	for c in cursor:
		weibo_content = c['weibo_content'].encode('gbk','ignore').decode('gbk','ignore')
		weibo_time = c['weibo_time'].encode('gbk','ignore').decode('gbk','ignore')
		writer.writerow([c['keyword'],c['nick_name'],c['user_homepage'],\
			c['weibo_href'],\
			weibo_content,\
			weibo_time])
	csvfile.close()

def output_user_information_entry():
	cfg = getconfig()
	Collection_UserHomePages = cfg['Collections']['SearchWeibo']
	dbo = dboperator.Dboperator(collname = Collection_UserHomePages)

	db_name = cfg['MongoDBConnection']['db']
	output_dir = 'DATA//' + db_name
	DirOperator.DirOperator(output_dir)

	output_filename = output_dir+'//search_weibo.csv'
	output_user_information(dbo,output_filename)
	dbo.connclose()

def main():
	output_user_information_entry()

