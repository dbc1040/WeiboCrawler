#coding:utf-8
from weibocrawler import dboperator
from weibocrawler.config import getconfig
from weibocrawler import DirOperator
import csv
# def output_user_information(dbo,output_filename):
# 	csvfile = open(output_filename,'w',newline="")
# 	writer = csv.writer(csvfile,dialect='excel')
# 	writer.writerow(['主页', '昵称', '用户ID','微博数',\
# 		'地址','性别','生日','简介','注册日期'])

# 	cursor = dbo.coll.find({},{"href":1,"nickName":1,"userId":1,'weiboNum':1,"address":1,\
# 		"gender":1,"birthday":1,"introduction":1,"registrationDate":1})

# 	for c in cursor:
# 		# inf_list = list()
# 		writer.writerow([c['href'],c['nickName'],c['userId'],c['weiboNum'],c['address'],\
# 			c['gender'],c['birthday'],c['introduction'],c['registrationDate']])
# 	csvfile.close()
def output_user_information(dbo,output_filename):
	csvfile = open(output_filename,'w',newline="")
	writer = csv.writer(csvfile,dialect='excel')
	writer.writerow(['主页', '昵称', '用户ID','微博数','粉丝数','关注数'])

	cursor = dbo.coll.find({},{"href":1,"nickName":1,"userId":1,'weiboNum':1,'followerNum':1,'followeeNum':1})

	for c in cursor:
		# inf_list = list()
		href = c.get('href','')
		nickName = c.get('nickName','')
		userId = c.get('userId','')
		weiboNum = c.get('weiboNum','')
		followerNum = c.get('followerNum','')
		followeeNum = c.get('followeeNum','')
		if href == '' or nickName == '' or userId == '' \
			or weiboNum == '' or followerNum == '' or followeeNum == '':
			continue
		writer.writerow([href,nickName,userId,weiboNum,followerNum,followeeNum])
	csvfile.close()

def output_user_information_entry():
	cfg = getconfig()
	Collection_UserHomePages = cfg['Collections']['UserHomePages']
	dbo = dboperator.Dboperator(collname = Collection_UserHomePages)
	db_name = cfg['MongoDBConnection']['db']
	output_dir = 'DATA//' + db_name
	DirOperator.DirOperator(output_dir)

	output_filename = output_dir + '//user_information.csv'
	output_user_information(dbo,output_filename)
	dbo.connclose()

# if __name__ == '__main__':
# 	output_user_information_entry()

