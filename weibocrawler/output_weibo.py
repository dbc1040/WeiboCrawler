#coding:utf-8
from weibocrawler import conver_mid_url
from weibocrawler import dboperator
from weibocrawler import DirOperator
from weibocrawler.config import getconfig
import csv


def print_weibo_content(dbo,Weibo_dir):
	output_weibo_content = Weibo_dir + 'weibo_content.csv'
	csvfile_weibo_content = open(output_weibo_content,'w',newline="")
	writer_weibo_content = csv.writer(csvfile_weibo_content,dialect='excel')
	writer_weibo_content.writerow(['用户ID', '微博链接', '微博内容','发博时间','发博方式',\
		'微博类型','原微博链接','原博主ID'])
	cursor = dbo.coll.find({},{"userId":1,'mId':1,"text": 1,'dateFormart':1,'fromText':1,\
		'isForward':1,"oMId":1,'oUserId':1})
	content_dic = {}
	for c in cursor:
		userId = c['userId']
		weibo_url = 'http://weibo.com/'+str(userId)+'/'+ conver_mid_url.mid_to_url(c['mId'])
		text = c['text'].encode('gbk','ignore').decode('gbk','ignore')
		dateFormart = c['dateFormart']
		fromText = c['fromText'].encode('gbk','ignore').decode('gbk','ignore')
		if c['isForward'] == '1':
			weibo_type = '转发微博'
			oUserId = c['oUserId']
			oMId = 'http://weibo.com/'+str(oUserId)+'/'+ conver_mid_url.mid_to_url(c['oMId'])
		else:
			weibo_type = '原创微博'
			oUserId = -1
			oMId = -1

		writer_weibo_content.writerow([userId,weibo_url,text,dateFormart,fromText,\
			weibo_type,oMId,oUserId])

		if userId in content_dic.keys():
			if dateFormart > content_dic[userId]['dateFormart']:
				content_dic[userId]['weibo_url'] = weibo_url
				content_dic[userId]['rct_weibo_content'] = text.strip()
				content_dic[userId]['dateFormart'] = dateFormart
				content_dic[userId]['fromText'] = fromText
				content_dic[userId]['weibo_type'] = weibo_type
				content_dic[userId]['oMId'] = oMId
				content_dic[userId]['oUserId'] = oUserId
		else:
			content_dic[userId] = {}
			content_dic[userId]['weibo_url'] = weibo_url
			content_dic[userId]['rct_weibo_content'] = text.strip()
			content_dic[userId]['dateFormart'] = dateFormart
			content_dic[userId]['fromText'] = fromText
			content_dic[userId]['weibo_type'] = weibo_type
			content_dic[userId]['oMId'] = oMId
			content_dic[userId]['oUserId'] = oUserId
	csvfile_weibo_content.close()

	output_recent_weibo = Weibo_dir + 'recent_weibo.csv'
	csvfile_recent_weibo = open(output_recent_weibo,'w',newline="")
	writer_recent_weibo = csv.writer(csvfile_recent_weibo,dialect='excel')
	writer_recent_weibo.writerow(['用户ID', '微博链接', '微博内容','发博时间','发博方式',\
		'微博类型','原微博链接','原博主ID'])
	for userId in content_dic.keys():
		writer_recent_weibo.writerow([userId,\
			content_dic[userId]['weibo_url'],\
			content_dic[userId]['rct_weibo_content'],\
			content_dic[userId]['dateFormart'],\
			content_dic[userId]['fromText'],\
			content_dic[userId]['weibo_type'],\
			content_dic[userId]['oMId'],\
			content_dic[userId]['oUserId']])
	csvfile_recent_weibo.close()
	return

def main():
	cfg = getconfig()
	Collection_UserTimelinePages = cfg['Collections']['UserTimelines']
	dbo = dboperator.Dboperator(collname = Collection_UserTimelinePages)

	db_name = cfg['MongoDBConnection']['db']
	output_dir = 'DATA//' + db_name
	DirOperator.DirOperator(output_dir)
	Weibo_dir = output_dir+'//'
	
	print_weibo_content(dbo,Weibo_dir)
	dbo.connclose()


