# Covert_cookies.py
# 为了应对无法从weibo获取cookie的问题，手工制作cookies
# 	输入：cookies.txt  手工把Chrome中的cookies信息复制到cookies中
#   输出: cookies.json 抽取cookies_copy中的信息生成新的cookies.json
# 原有的cookies.json备份到cookies.json_backup中 
# doufunao
# 2014-03-13
#
import json
import shutil
def convert_cookies():
	shutil.copyfile('INPUT//cookies.json', 'INPUT//cookies.json_backup')
	string = open('INPUT//cookies.txt', 'r').read()
	cookies_dict_new = {}
	cookies_dict_old = json.loads(open('INPUT//cookies_template', 'r').read())

	for a_dict_string in string.split(';'):
		loc = a_dict_string.find('=')
		key = a_dict_string[0:loc].strip()
		value = a_dict_string[loc+1:len(a_dict_string)]
		if key in cookies_dict_old:
			cookies_dict_new[key] = value

	dict_dumps = json.dumps(cookies_dict_new)
	open('INPUT//cookies.json', 'w').write(dict_dumps)
	print('>.< Have successfully created cookies.json by hand!')

