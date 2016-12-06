import configparser
def getconfig():
	config = configparser.ConfigParser()
	config.read('INPUT//config.txt')
	return config

# if __name__ == '__main__':
# 	cfg = getconfig()
# 	print(type(cfg))