#coding:utf-8
import re
from weibocrawler import dboperator
from weibocrawler import DirOperator
from weibocrawler.config import getconfig
import csv

#函数作用是从text中提取出昵称字段，存放在列表中返回
#输入：文本text
#输出：昵称列表
def ExtractNamesfromText(text):
	namelist = list()
	text_temp = text
	nick_pattern = re.compile(r'@([0-9a-zA-Z\u4e00-\u9fa5_-]*)')
	if nick_pattern.search(text) != None:
		names = nick_pattern.findall(text)
		for name in names:
			if len(name) > 15:
				continue
			if name not in namelist:
				namelist.append(name)
	return namelist
#函数作用是从数据库中提取昵称，存放在文件中
#输入：数据库的集合collection名称,源UserId
#输出：昵称列表文件namelsit.txt
def ExtractNickNamesfromDB(dbo,Weibo_dir):
	output_new_users = Weibo_dir + 'new_users.csv'
	csvfile_new_users = open(output_new_users,'w',newline="")
	writer_new_users = csv.writer(csvfile_new_users,dialect='excel')
	writer_new_users.writerow(['用户ID','发现用户'])
	cursor = dbo.coll.find({},{"userId":1,"text": 1})
	NickName_list = list()
	for c in cursor:
		userId = c['userId']
		text = c['text']
		namelist = ExtractNamesfromText(text)
		for name in namelist:
			if name not in NickName_list:
				NickName_list.append(name)
				writer_new_users.writerow([userId,name])
	csvfile_new_users.close()

def main():
	cfg = getconfig()
	Collection_UserTimelinePages = cfg['Collections']['UserTimelines']
	dbo = dboperator.Dboperator(collname = Collection_UserTimelinePages)

	db_name = cfg['MongoDBConnection']['db']
	output_dir = 'DATA//' + db_name
	DirOperator.DirOperator(output_dir)
	Weibo_dir = output_dir+'//'
	
	ExtractNickNamesfromDB(dbo,Weibo_dir)
