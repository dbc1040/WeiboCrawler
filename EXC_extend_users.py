from weibocrawler import get_user_relationship
from weibocrawler import proc_user_relation_pages
from weibocrawler import output_extend_users
from weibocrawler.convert_cookies import convert_cookies
from weibocrawler import WeiboHttpRequest
from weibocrawler import WeiboLogin
from weibocrawler import log

def get_request(check_cookie_file = True):
	username = ''
	password = ''
	if check_cookie_file == True:
		convert_cookies()
	login = WeiboLogin(username, password)
	http_request = WeiboHttpRequest(login)
	return http_request

def main():
	request = get_request()

	log("get user relationship","start!")
	get_user_relationship.main(request)
	log("get user relationship","succeed!")

	log("proc user relationship","start!")
	proc_user_relation_pages.main()
	log("proc user relationship","succeed!")

	log("output extend users","start!")
	output_extend_users.main()
	log("output extend users","succeed!")

main()
