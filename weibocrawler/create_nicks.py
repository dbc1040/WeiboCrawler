from weibocrawler import dboperator
from weibocrawler.config import getconfig
def create_nicks(file_name, dbo):
	fr = open(file_name, "r", encoding = "utf-8")
	for l in fr.readlines():
		line = l.strip()
		tag = 'http://weibo.com/'
		if line.find(tag) == -1:
			href = "http://weibo.com/" + str(line)
		else:
			href = line
		dbo.coll.update({'href': href},{'$set': {'href': href}}, upsert = True)
'''
This function will crawler user page read from collection Nicks and insert them into collection UserHomePages from MongoDB.
'''
def create_nicks_entry():
	cfg = getconfig()

	# 把文件中的userid导入数据库
	file_name = "INPUT//SeedUserList.txt"

	Collection_Nicks = cfg['Collections']['Nicks'] #"Nicks_iter02_10_06"# get href	

	dbo = dboperator.Dboperator(collname = Collection_Nicks)
	

	create_nicks(file_name, dbo)
	dbo.connclose()
# if __name__ == '__main__':
# 	create_nicks_entry()

def search2nick():
	cfg = getconfig()
	Collection_Nicks = cfg['Collections']['Nicks'] 
	Collection_search = cfg['Collections']['SearchPages']
	Collection_UserHomePage = cfg['Collections']['UserHomePages']

	dbo1 = dboperator.Dboperator(collname = Collection_Nicks)
	dbo2 = dboperator.Dboperator(collname = Collection_search)
	dbo3 = dboperator.Dboperator(collname = Collection_UserHomePage)

	cursor_search = dbo2.coll.find({},{'querystring':1,'user_href':1})
	cursor_User = dbo3.coll.find({},{'nickName':1})
	nickName_list = []
	for c in cursor_User:
		nick = c.get('nickName','')
		if nick == '':
			continue
		if nick not in nickName_list:
			nickName_list.append(nick)
	print(nickName_list)
	for cursor in cursor_search:
		nick = cursor.get('querystring','')
		if nick == '':
			continue
		if nick in nickName_list:
			continue
		url = cursor.get('user_href','')
		if url == None or url == '':
			continue
		print('nick:'+nick)
		print('url :'+url)
		dbo1.coll.update({'href': url},{'$set': {'href': url}}, upsert = True)

	dbo1.connclose()
	dbo2.connclose()
	dbo3.connclose()
# if __name__ == '__main__':
# 	search2nick()