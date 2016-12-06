#coding:utf-8
from weibocrawler import dboperator
from weibocrawler import DirOperator
from weibocrawler.config import getconfig
from networkx import *
import networkx as nx
import csv

'''得到种子群体UserId'''
def getUserId():
	cfg = getconfig()
	Collection_UserHomePages = cfg['Collections']['UserHomePages']
	dbo = dboperator.Dboperator(collname = Collection_UserHomePages)
	userIds = dbo.coll.distinct("userId")
	# print(len(userIds))
	return userIds

def output_extend_users(dbo,extend_users_dir):
	cursor = dbo.coll.find({},{"followeeId":1, "userId": 1})
	edge_list = list()
	for c in cursor:
		# str_pair = str(c["userId"])+","+str(c["followeeId"])
		# t = tuple(str_pair.split(','))
		t = (c["userId"],c["followeeId"])
		edge_list.append(t)
	G = nx.DiGraph()
	G.add_edges_from(edge_list)
	G1 = nx.Graph(G)
	dict_x = clustering(G1)
	sort_x = sorted(dict_x.items(), key=lambda item: item[1], reverse=True)
	userIds = getUserId()

	output_filename = extend_users_dir + 'extend_users.csv'
	csvfile = open(output_filename,'w',newline="")
	writer = csv.writer(csvfile,dialect='excel')
	writer.writerow(['用户ID', '权重'])

	for x, y in sort_x:
		# print(str(x)+':'+str(y))
		if x  in userIds:
			continue
		else:
			if y > 0:
				writer.writerow([str(x), str(y)])
	csvfile.close()

def main():
	cfg = getconfig()
	Collection_UserRelations = cfg['Collections']['UserRelations']
	dbo = dboperator.Dboperator(collname = Collection_UserRelations)

	db_name = cfg['MongoDBConnection']['db']
	output_dir = 'DATA//' + db_name
	DirOperator.DirOperator(output_dir)
	extend_users_dir = output_dir+'//'
	
	output_extend_users(dbo,extend_users_dir)
	dbo.connclose()
