from weibocrawler.convert_cookies import convert_cookies
from weibocrawler import WeiboHttpRequest
from weibocrawler import WeiboLogin
from weibocrawler import log
from weibocrawler.create_nicks import create_nicks_entry
from weibocrawler.get_user_pages import get_user_home_pages_entry
from weibocrawler.output_information import output_user_information_entry
from weibocrawler.proc_user_pages import proc_user_pages_entry
def get_request(check_cookie_file = True):
	username = '111111111'
	password = '11111111111'
	if check_cookie_file == True:
		convert_cookies()
	login = WeiboLogin(username, password)
	http_request = WeiboHttpRequest(login)
	return http_request

def main():

	# input_a = input("input any key to start:")
	# print (input_a)
	request = get_request()
	log("creating nicks","start!")
	create_nicks_entry()
	log("creating nicks","succeed!")

	log("get user pages","start!")
	get_user_home_pages_entry(request)
	log("get user pages","succeed!")

	proc_user_pages_entry(request)

	log("output user information","start!")
	output_user_information_entry()
	log("output user information","succeed!")


	# input_b = input("input any key to end:")

main()
