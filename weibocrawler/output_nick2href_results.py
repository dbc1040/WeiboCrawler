#coding:utf-8
from weibocrawler import dboperator
from weibocrawler import DirOperator
from weibocrawler.config import getconfig
import csv
def output_user_information(dbo,output_filename):
	csvfile = open(output_filename,'w',newline="")
	writer = csv.writer(csvfile,dialect='excel')
	writer.writerow(['用户昵称', '用户主页'])

	cursor = dbo.coll.find({},{"querystring":1,"user_href":1})
	for c in cursor:
		user_href = c.get("user_href",'')
		if user_href == '':
			continue
		querystring = c['querystring'].encode('gbk','ignore').decode('gbk','ignore')
		user_href = user_href.encode('gbk','ignore').decode('gbk','ignore')
		writer.writerow([querystring,user_href])
	csvfile.close()

def output_user_information_entry():
	cfg = getconfig()
	Collection_UserHomePages = cfg['Collections']['SearchPages']
	dbo = dboperator.Dboperator(collname = Collection_UserHomePages)

	db_name = cfg['MongoDBConnection']['db']
	output_dir = 'DATA//' + db_name
	DirOperator.DirOperator(output_dir)

	output_filename = output_dir+'//nick2href_result.csv'
	output_user_information(dbo,output_filename)
	dbo.connclose()

def main():
	output_user_information_entry()

