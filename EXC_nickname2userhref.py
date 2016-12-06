from weibocrawler import create_search_keywords
from weibocrawler import get_search_results_onepage
from weibocrawler import proc_search_results_onepage
from weibocrawler import output_nick2href_results
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

	log("create search keywords","start!")
	create_search_keywords.main()
	log("create search keywords","succeed!")

	log("get search results","start!")
	get_search_results_onepage.main(request)
	log("get search results","succeed!")

	log("proc search results","start!")
	proc_search_results_onepage.main()
	log("proc search results","succeed!")

	log("output search results","start!")
	output_nick2href_results.main()
	log("output search results","succeed!")

main()
