from weibocrawler import get_user_timeline
from weibocrawler import proc_user_timeline_pages
from weibocrawler.convert_cookies import convert_cookies
from weibocrawler import WeiboHttpRequest
from weibocrawler import WeiboLogin
from weibocrawler import log
from weibocrawler import output_weibo
from weibocrawler import ExtractNickNames
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

	log("get user weibo","start!")
	get_user_timeline.main(request)
	log("get user weibo","succeed!")

	log("proc user weibo","start!")
	proc_user_timeline_pages.main()
	log("proc user weibo","succeed!")

	log("output weibo content",'start!')
	output_weibo.main()
	log("output weibo content",'succeed!')

	log("Extract new users","start!")
	ExtractNickNames.main()
	log("Extract new users","succeed!")

main()
